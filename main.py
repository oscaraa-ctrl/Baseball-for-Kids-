
from drafter import *
from dataclasses import dataclass
import random


# SECOND DATACLASS
@dataclass
class AtBatters:
    pitch_location: str
    grid_location: str
    ball_speed: float
    points_at_bat: int
    result: str
    distance: int


# STATE DATACLASS
@dataclass
class State:
    batting_player: list[AtBatters]
    total_score: int
    batter_eye_focus: int
    bat_strength: int
    bat_type: str
    pitcher_strength: float
    current_inning: int
    pitch_location: str
    target_row: int
    target_col: int
    misses: int


# ROUTE 1: START PAGE
@route
def index(state: State) -> Page:
    return Page(state, [
        Header("BASEBALL 4 KIDZ"),
        Header("Baseball Simulator"),
        "Welcome to BASEBALL 4 KIDZ!",
        "",
        "Create your own baseball player, choose your bat,",
        "face a pitcher, and see how far you can hit!",
        "",
        Button("START GAME", "batter_custom")
    ])


# ROUTE 2: BATTER CUSTOMIZATION
@route
def batter_custom(state: State) -> Page:
    return Page(state, [
        Header("CREATE YOUR BATTER"),
        "Customize your player's abilities.",
        "",
        "Batter Strength (1-1000):",
        TextBox("batter_strength", 500, "number"),
        "",
        "Eye Focus (1-100):",
        TextBox("batter_eye_focus", 50, "number"),
        "",
        Button("Continue", "save_batter")
    ])


# ROUTE 3: SAVE BATTER INFORMATION
@route
def save_batter(state: State, batter_strength: int,
                batter_eye_focus: int) -> Page:

    if batter_strength > 1000:
        batter_strength = 1000

    if batter_strength < 1:
        batter_strength = 1

    if batter_eye_focus > 100:
        batter_eye_focus = 100

    if batter_eye_focus < 1:
        batter_eye_focus = 1

    state.bat_strength = batter_strength
    state.batter_eye_focus = batter_eye_focus

    return bat_custom(state)


# ROUTE 4: BAT CUSTOMIZATION
@route
def bat_custom(state: State) -> Page:
    return Page(state, [
        Header("CHOOSE YOUR BAT"),
        "Each material changes how much energy",
        "is transferred to the baseball.",
        "",
        "Wood: Standard power",
        "Metal: Increased power",
        "Paper: Reduced power",
        "",
        "Choose your bat:",
        SelectBox(
            "bat_type",
            ["wood", "metal", "paper"],
            state.bat_type
        ),
        "",
        Button("Continue", "save_bat")
    ])


# ROUTE 5: SAVE BAT INFORMATION
@route
def save_bat(state: State, bat_type: str) -> Page:
    state.bat_type = bat_type
    return pitcher_custom(state)


# ROUTE 6: PITCHER CUSTOMIZATION
@route
def pitcher_custom(state: State) -> Page:
    return Page(state, [
        Header("CHOOSE YOUR PITCHER"),
        "How fast will the pitcher throw?",
        "",
        "Enter a speed between 1 and 105.8 mph.",
        "",
        "Pitch Speed:",
        TextBox(
            "pitcher_speed",
            state.pitcher_strength,
            "number"
        ),
        "",
        Button("Start Batting!", "save_pitcher")
    ])


# ROUTE 7: SAVE PITCHER INFORMATION
@route
def save_pitcher(state: State, pitcher_speed: float) -> Page:

    if pitcher_speed >= 105.8:
        return Page(state, [
            Header("PITCH TOO FAST!"),
            "Pitch must be lower than 105.8 mph.",
            TextBox("pitcher_speed", pitcher_speed, "number"),
            Button("Try Again", "save_pitcher")
        ])

    if pitcher_speed < 1:
        return Page(state, [
            Header("INVALID PITCH"),
            "Pitch speed must be at least 1 mph.",
            TextBox("pitcher_speed", pitcher_speed, "number"),
            Button("Try Again", "save_pitcher")
        ])

    state.pitcher_strength = pitcher_speed

    return actual_batting(state)


# ROUTE 8: CREATE THE 10x10 GRID
@route
def actual_batting(state: State) -> Page:

    # Randomly position the green 3x3 hitting zone
    state.target_row = random.randint(0, 7)
    state.target_col = random.randint(0, 7)

    grid = []

    for row in range(10):
        grid_row = []

        for col in range(10):

            # Check whether this square is inside the green zone
            if (state.target_row <= row < state.target_row + 3
                    and state.target_col <= col < state.target_col + 3):

                cell_color = "#39B54A"

            else:
                cell_color = "#DDDDDD"

            # Create a button for each square
            cell = Button(
                " ",
                "final_score",
                arguments=[
                    ("selected_row", row),
                    ("selected_col", col)
                ],
                style_background_color=cell_color,
                style_width="35px",
                style_height="35px",
                style_padding="0px",
                style_border="1px solid black"
            )

            grid_row.append(cell)

        grid.append(grid_row)

    return Page(state, [
        Header("CHOOSE YOUR SWING!"),
        "",
        "Select ONE square on the field.",
        "Green = Hitting Zone",
        "Gray = Outside the Hitting Zone",
        "",
        "Misses this inning: " + str(state.misses) + " / 3",
        "",
        Table(grid)
    ])


# ROUTE 9: CALCULATE THE BATTING RESULTS
@route
def final_score(state: State, selected_row: int,
                selected_col: int) -> Page:

    # Describe the selected square
    grid_location = (
        "Row " + str(selected_row + 1) +
        ", Column " + str(selected_col + 1)
    )

    # Check whether the selected square is inside the green zone
    if (state.target_row <= selected_row < state.target_row + 3
            and state.target_col <= selected_col < state.target_col + 3):

        contact = True

    else:
        contact = False

    # Default values
    distance = 0
    points = 0

    if contact:

        # Bat material multiplier
        if state.bat_type == "metal":
            bat_multiplier = 1.15

        elif state.bat_type == "paper":
            bat_multiplier = 0.45

        else:
            bat_multiplier = 1.0

        # Eye focus multiplier
        focus_multiplier = 0.8 + (state.batter_eye_focus / 500)

        # Calculate distance from the center of the green zone
        row_difference = abs(
            selected_row - (state.target_row + 1)
        )

        col_difference = abs(
            selected_col - (state.target_col + 1)
        )

        if row_difference == 0 and col_difference == 0:
            location_multiplier = 1.0

        elif row_difference == 1 and col_difference == 1:
            location_multiplier = 0.75

        else:
            location_multiplier = 0.85

        # Calculate how far the ball travels
        distance = int(
            state.bat_strength *
            0.45 *
            bat_multiplier *
            focus_multiplier *
            location_multiplier
        )

        # Determine the hit result and points
        if distance < 50:
            result = "Weak Contact"
            points = 1

        elif distance < 150:
            result = "Ground Ball"
            points = 2

        elif distance < 250:
            result = "Line Drive"
            points = 3

        elif distance < 350:
            result = "Deep Fly Ball"
            points = 4

        else:
            result = "HOME RUN!"
            points = 5

    else:
        # A miss increases the miss counter
        result = "MISSED BALL!"
        state.misses += 1

    # Save this attempt in the batting history
    attempt = AtBatters(
        "Random hitting zone",
        grid_location,
        state.pitcher_strength,
        points,
        result,
        distance
    )

    state.batting_player.append(attempt)

    # Add points to the overall score
    state.total_score += points

    # Calculate the ball's landing position
    landing_cell = int(distance / 5)

    if landing_cell > 99:
        landing_cell = 99

    # Create the 10x10 landing field
    field_display = ""

    for row in range(10):

        for column in range(10):

            cell_number = row * 10 + column

            if distance > 0 and cell_number == landing_cell:
                field_display += " X "

            else:
                field_display += " . "

        field_display += "\n"

    # Display batting history
    history = ""
    attempt_number = 0

    for previous_attempt in state.batting_player:

        attempt_number += 1

        history += (
            "Attempt " + str(attempt_number) +
            ": " + previous_attempt.result +
            " | " + str(previous_attempt.distance) +
            " feet | " +
            str(previous_attempt.points_at_bat) +
            " points\n"
        )

    # Common results page content
    page_content = [
        Header("BATTING RESULTS"),
        "",
        "Your selection: " + grid_location,
        "Pitch speed: " + str(state.pitcher_strength) + " mph",
        "",
        Header(result),
        "Distance: " + str(distance) + " feet",
        "Points earned: " + str(points),
        "",
        "Misses this inning: " + str(state.misses) + " / 3",
        "",
        Header("BALL LANDING FIELD"),
        "X = Ball landing location",
        field_display,
        "",
        Header("SCOREBOARD"),
        "Current inning: " + str(state.current_inning),
        "Total score: " + str(state.total_score),
        "",
        Header("BATTING HISTORY"),
        history,
        ""
    ]

    # Show different buttons depending on the number of misses
    if state.misses < 3:

        page_content.append(
            Button("Swing Again", "actual_batting")
        )

    else:

        page_content.append(
            Header("THREE MISSES! INNING OVER!")
        )

        page_content.append(
            Button("Next Inning", "one_more_inning")
        )

        page_content.append(
            Button("Finish Game", "finish_game")
        )

    page_content.append(
        Button("Restart Game", "restart")
    )

    return Page(state, page_content)


# ROUTE 10: NEXT INNING
@route
def one_more_inning(state: State) -> Page:

    # Increase the inning number
    state.current_inning += 1

    # Reset the misses for the new inning
    state.misses = 0

    return actual_batting(state)


# ROUTE 11: FINISH GAME
@route
def finish_game(state: State) -> Page:

    return Page(state, [
        Header("GAME OVER!"),
        "",
        "Final Score: " + str(state.total_score),
        "Innings Played: " + str(state.current_inning),
        "Total Swings: " + str(len(state.batting_player)),
        "",
        Button("Play Again", "restart")
    ])


# ROUTE 12: RESTART GAME
@route
def restart(state: State) -> Page:

    state.batting_player = []
    state.total_score = 0
    state.batter_eye_focus = 50
    state.bat_strength = 500
    state.bat_type = "wood"
    state.pitcher_strength = 60.0
    state.current_inning = 1
    state.pitch_location = ""
    state.target_row = 0
    state.target_col = 0
    state.misses = 0

    return index(state)


# START THE WEBSITE
start_server(State(
    [],
    0,
    50,
    500,
    "wood",
    60.0,
    1,
    "",
    0,
    0,
    0
))
