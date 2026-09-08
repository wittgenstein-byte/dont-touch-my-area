import turtle
import time
from collections import deque

SCREEN_SIZE = 600
GRID_SIZE = 40
COLS = SCREEN_SIZE // GRID_SIZE  # 15 columns (600 // 40)
ROWS = SCREEN_SIZE // GRID_SIZE  # 15 rows (600 // 40)

# Cell state values in the 2D array:
# 0 = Empty cell
# 1 = Player 1 permanent territory, 2 = Player 2 permanent territory
# 3 = Player 1 temporary trail,     4 = Player 2 temporary trail
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# ===========================================
# SCREEN & RENDERER SETUP
# ===========================================
wn = turtle.Screen()
wn.title("2D Array Territory Fill")
wn.bgcolor("#1a1a1a")
wn.setup(width=SCREEN_SIZE, height=SCREEN_SIZE)
wn.tracer(0)

# Turtle used to draw grid squares according to the matrix values
drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)
drawer.shape("square")
drawer.shapesize(stretch_wid=GRID_SIZE / 20, stretch_len=GRID_SIZE / 20)
drawer.penup()

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
    Called when a loop is closed:
    1. Run a flood fill (BFS) from the matrix outer borders inward (unclaimed space).
    2. Any internal cell unreachable by the flood fill, plus the trail itself,
       is captured and converted to the player's permanent territory.
    """
    # Enclosure boundary = current player's territory or active trail
    boundary_values = {player_id, trail_id}
    
    visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
    queue = deque()

    # Seed the BFS queue with non-boundary cells along the left and right edges
    for r in range(ROWS):
        for c in [0, COLS - 1]:
            if grid[r][c] not in boundary_values:
                visited[r][c] = True
                queue.append((r, c))
                
    # Seed the BFS queue with non-boundary cells along the top and bottom edges
    for c in range(COLS):
        for r in [0, ROWS - 1]:
            if grid[r][c] not in boundary_values and not visited[r][c]:
                visited[r][c] = True
                queue.append((r, c))

    # Flood-fill only the outer exterior region
    while queue:
        cr, cc = queue.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = cr + dr, cc + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if not visited[nr][nc] and grid[nr][nc] not in boundary_values:
                    visited[nr][nc] = True
                    queue.append((nr, nc))

    # Update matrix: Any cell not reached by the outer flood fill (enclosed)
    # or belonging to the trail is converted into permanent territory.
    for r in range(ROWS):
        for c in range(COLS):
            if not visited[r][c] or grid[r][c] == trail_id:
                grid[r][c] = player_id

def render_grid():
    """Redraws the grid on screen based on the 2D matrix state."""
    drawer.clear()
    COLOR_MAP = {
        1: "#e74c3c",  # P1 permanent territory (dark red)
        3: "#ff7675",  # P1 temporary trail (light red)
        2: "#0984e3",  # P2 permanent territory (dark blue)
        4: "#74b9ff"   # P2 temporary trail (light blue)
    }
    for r in range(ROWS):
        for c in range(COLS):
            val = grid[r][c]
            if val in COLOR_MAP:
                x, y = grid_to_screen(r, c)
                drawer.goto(x, y)
                drawer.color(COLOR_MAP[val])
                drawer.stamp()

# ===========================================
# PLAYER SETUP
# ===========================================
p1 = turtle.Turtle()
p1.shape("square")
p1.color("white", "#c0392b")
p1.penup()
p1.direction = "stop"

# Set P1 starting position
start_r, start_c = ROWS // 2, COLS // 4
p1.goto(grid_to_screen(start_r, start_c))
grid[start_r][start_c] = 1

# ===========================================
# CONTROLS
# ===========================================
def go_up():
    if p1.direction != "down": p1.direction = "up"
def go_down():
    if p1.direction != "up": p1.direction = "down"
def go_left():
    if p1.direction != "right": p1.direction = "left"
def go_right():
    if p1.direction != "left": p1.direction = "right"

wn.listen()
wn.onkeypress(go_up, "Up")
wn.onkeypress(go_down, "Down")
wn.onkeypress(go_left, "Left")
wn.onkeypress(go_right, "Right")
wn.onkeypress(go_up, "w")
wn.onkeypress(go_down, "s")
wn.onkeypress(go_left, "a")
wn.onkeypress(go_right, "d")

# ===========================================
# GAME LOOP
# ===========================================
while True:
    if p1.direction != "stop":
        curr_r, curr_c = screen_to_grid(p1.xcor(), p1.ycor())
        
        # Calculate next step coordinates
        next_r, next_c = curr_r, curr_c
        if p1.direction == "up": next_r -= 1
        elif p1.direction == "down": next_r += 1
        elif p1.direction == "left": next_c -= 1
        elif p1.direction == "right": next_c += 1

        # Keep movement within screen boundaries
        if 0 <= next_r < ROWS and 0 <= next_c < COLS:
            target_cell = grid[next_r][next_c]
            
            # Move player head
            p1.goto(grid_to_screen(next_r, next_c))

            # Check if player hits their own trail (3) or returns to territory (1)
            if target_cell in (1, 3):
                # Fill enclosed area and convert trail to territory
                close_loop_and_fill(player_id=1, trail_id=3)
            else:
                # Mark empty cell as active trail
                grid[next_r][next_c] = 3

    render_grid()
    wn.update()
    time.sleep(0.1)