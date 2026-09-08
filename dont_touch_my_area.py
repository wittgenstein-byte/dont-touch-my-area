import turtle
import time
from collections import deque

# ===========================================
# SCREEN & RESOLUTION GRID SETTINGS
# ===========================================
SCREEN_SIZE = 600
GRID_SIZE = 15                  # Smaller tile size = finer resolution
COLS = SCREEN_SIZE // GRID_SIZE  # 40 columns
ROWS = SCREEN_SIZE // GRID_SIZE  # 40 rows
TOTAL_CELLS = ROWS * COLS       # 1,600 total playable tiles

# Cell states:
# 0 = Empty, 1 = P1 Territory, 2 = P2 Territory
# 3 = P1 Trail, 4 = P2 Trail
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Track only changed cells so rendering 1600+ tiles stays fast and smooth
dirty_cells = set()

def set_cell(r, c, val):
    """Updates a grid cell and queues it for efficient redraw."""
    if grid[r][c] != val:
        grid[r][c] = val
        dirty_cells.add((r, c))

# ===========================================
# SCREEN & RENDERER SETUP
# ===========================================
wn = turtle.Screen()
wn.title("Don't Touch My Area - Territory Conquest")
wn.bgcolor("#1a1a1a")
wn.setup(width=SCREEN_SIZE + 40, height=SCREEN_SIZE + 90)  # Added top margin for HUD
wn.tracer(0)

# Stamp pool turtle (stamps only modified tiles)
stamper = turtle.Turtle()
stamper.hideturtle()
stamper.speed(0)
stamper.shape("square")
stamper.shapesize(stretch_wid=GRID_SIZE / 20, stretch_len=GRID_SIZE / 20)
stamper.penup()

# Keep track of stamps per coordinate so old stamps can be cleared
tile_stamps = {}

# ===========================================
# SCOREBOARD SETUP
# ===========================================
pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.color("white")
pen.penup()
pen.goto(0, (SCREEN_SIZE / 2) + 12)

# Keep track of prior scores to avoid redrawing text every tick
last_score_p1 = -1
last_score_p2 = -1

def update_scoreboard():
    """Counts permanent territory cells and renders point totals when values change."""
    global last_score_p1, last_score_p2
    p1_tiles = sum(row.count(1) for row in grid)
    p2_tiles = sum(row.count(2) for row in grid)

    if p1_tiles != last_score_p1 or p2_tiles != last_score_p2:
        last_score_p1 = p1_tiles
        last_score_p2 = p2_tiles

        pen.clear()
        pen.write(
            f"P1 (Red): {p1_tiles} pts    |    P2 (Blue): {p2_tiles} pts",
            align="center",
            font=("Courier", 13, "bold")
        )
# ===========================================
# GRID COORDINATE HELPERS
# ===========================================
def screen_to_grid(x, y):
    """Converts screen pixel coordinates to matrix indices [row][col]."""
    c = int((x + (SCREEN_SIZE / 2)) // GRID_SIZE)
    r = int(((SCREEN_SIZE / 2) - y) // GRID_SIZE)
    return max(0, min(ROWS - 1, r)), max(0, min(COLS - 1, c))

def grid_to_screen(r, c):
    """Converts matrix indices [row][col] to screen center coordinates (x, y)."""
    x = (c * GRID_SIZE) - (SCREEN_SIZE / 2) + (GRID_SIZE / 2)
    y = (SCREEN_SIZE / 2) - (r * GRID_SIZE) - (GRID_SIZE / 2)
    return x, y

# ===========================================
# MATRIX FLOOD FILL LOGIC
# ===========================================
def close_loop_and_fill(player_id, trail_id):
    """
    Flood fills outside space from screen borders. Any cell unreachable
    by the fill (enclosed) + active trails becomes permanent territory.
    """
    boundary_values = {player_id, trail_id}
    visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
    queue = deque()

    # Border cells on left and right
    for r in range(ROWS):
        for c in [0, COLS - 1]:
            if grid[r][c] not in boundary_values:
                visited[r][c] = True
                queue.append((r, c))

    # Border cells on top and bottom
    for c in range(COLS):
        for r in [0, ROWS - 1]:
            if grid[r][c] not in boundary_values and not visited[r][c]:
                visited[r][c] = True
                queue.append((r, c))

    # Outer BFS flood fill
    while queue:
        cr, cc = queue.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = cr + dr, cc + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if not visited[nr][nc] and grid[nr][nc] not in boundary_values:
                    visited[nr][nc] = True
                    queue.append((nr, nc))

    # Convert enclosed cells and trail to permanent territory
    for r in range(ROWS):
        for c in range(COLS):
            if not visited[r][c] or grid[r][c] == trail_id:
                set_cell(r, c, player_id)

def render_dirty_cells():
    """Renders only cells that changed value to maintain high FPS."""
    COLOR_MAP = {
        0: "#1a1a1a",  # Background color to wipe cleared cells
        1: "#e74c3c",  # P1 permanent territory (dark red)
        3: "#ff7675",  # P1 trail (light red)
        2: "#0984e3",  # P2 permanent territory (dark blue)
        4: "#74b9ff"   # P2 trail (light blue)
    }

    while dirty_cells:
        r, c = dirty_cells.pop()
        val = grid[r][c]

        # Remove previous stamp at this cell if present
        if (r, c) in tile_stamps:
            stamper.clearstamp(tile_stamps[(r, c)])
            del tile_stamps[(r, c)]

        # Stamp new state
        if val in COLOR_MAP and val != 0:
            x, y = grid_to_screen(r, c)
            stamper.goto(x, y)
            stamper.color(COLOR_MAP[val])
            tile_stamps[(r, c)] = stamper.stamp()

# ===========================================
# PLAYER 1 SETUP (Red)
# ===========================================
p1 = turtle.Turtle()
p1.shape("square")
p1.shapesize(stretch_wid=GRID_SIZE / 20, stretch_len=GRID_SIZE / 20)
p1.color("white", "#c0392b")
p1.penup()
p1.direction = "stop"

p1_start_r, p1_start_c = ROWS // 2, COLS // 5
p1.goto(grid_to_screen(p1_start_r, p1_start_c))

# Spawn initial 3x3 territory base
for dr in [-1, 0, 1]:
    for dc in [-1, 0, 1]:
        set_cell(p1_start_r + dr, p1_start_c + dc, 1)

# ===========================================
# PLAYER 2 SETUP (Blue)
# ===========================================
p2 = turtle.Turtle()
p2.shape("square")
p2.shapesize(stretch_wid=GRID_SIZE / 20, stretch_len=GRID_SIZE / 20)
p2.color("white", "#0865ac")
p2.penup()
p2.direction = "stop"

p2_start_r, p2_start_c = ROWS // 2, (COLS * 4) // 5
p2.goto(grid_to_screen(p2_start_r, p2_start_c))

# Spawn initial 3x3 territory base
for dr in [-1, 0, 1]:
    for dc in [-1, 0, 1]:
        set_cell(p2_start_r + dr, p2_start_c + dc, 2)

# ===========================================
# CONTROLS
# ===========================================
def p1_up():
    if p1.direction != "down": p1.direction = "up"
def p1_down():
    if p1.direction != "up": p1.direction = "down"
def p1_left():
    if p1.direction != "right": p1.direction = "left"
def p1_right():
    if p1.direction != "left": p1.direction = "right"

def p2_up():
    if p2.direction != "down": p2.direction = "up"
def p2_down():
    if p2.direction != "up": p2.direction = "down"
def p2_left():
    if p2.direction != "right": p2.direction = "left"
def p2_right():
    if p2.direction != "left": p2.direction = "right"

wn.listen()
wn.onkeypress(p1_up, "w")
wn.onkeypress(p1_down, "s")
wn.onkeypress(p1_left, "a")
wn.onkeypress(p1_right, "d")

wn.onkeypress(p2_up, "Up")
wn.onkeypress(p2_down, "Down")
wn.onkeypress(p2_left, "Left")
wn.onkeypress(p2_right, "Right")

# ===========================================
# PLAYER STEP LOGIC
# ===========================================
def step_player(player_turtle, player_id, trail_id):
    if player_turtle.direction == "stop":
        return

    curr_r, curr_c = screen_to_grid(player_turtle.xcor(), player_turtle.ycor())
    next_r, next_c = curr_r, curr_c

    if player_turtle.direction == "up": next_r -= 1
    elif player_turtle.direction == "down": next_r += 1
    elif player_turtle.direction == "left": next_c -= 1
    elif player_turtle.direction == "right": next_c += 1

    # Grid boundaries check
    if 0 <= next_r < ROWS and 0 <= next_c < COLS:
        target_cell = grid[next_r][next_c]
        player_turtle.goto(grid_to_screen(next_r, next_c))

        if target_cell in (player_id, trail_id):
            close_loop_and_fill(player_id, trail_id)
        else:
            set_cell(next_r, next_c, trail_id)

# ===========================================
# INITIAL HUD DRAW & GAME LOOP
# ===========================================
update_scoreboard()

while True:
    step_player(p1, player_id=1, trail_id=3)
    step_player(p2, player_id=2, trail_id=4)

    render_dirty_cells()
    update_scoreboard()
    wn.update()
    time.sleep(0.04)