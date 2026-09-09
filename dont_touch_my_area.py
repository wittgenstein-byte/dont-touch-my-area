import turtle
import time
from collections import deque

# ===========================================
# SCREEN & RESOLUTION GRID SETTINGS
# ===========================================
# 100 x 100 tiles (10,000 total tiles)
COLS = 100
ROWS = 100
TOTAL_CELLS = ROWS * COLS

# Tile size (in pixels).
# 6px per tile gives a 600x600 px arena.
# Window size is 640x690 px, which fits comfortably on any screen without overflowing.
GRID_SIZE = 6
SCREEN_SIZE = COLS * GRID_SIZE  # 600 pixels

# Cell states:
# 0 = Empty, 1 = P1 Territory, 2 = P2 Territory
# 3 = P1 Trail, 4 = P2 Trail
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Track only changed cells so rendering 10,000 tiles stays fast and smooth
dirty_cells = set()

# Game Management States: "MENU", "PLAYING", "GAME_OVER"
game_state = "MENU"
selected_time = 30  # Default 30 seconds
time_left = 30
start_time_stamp = 0

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

# UI Pen for Menu, Scoreboard, and Game Over
pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.penup()

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

# ===========================================
# RENDERING
# ===========================================
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
# PLAYER SETUP
# ===========================================
p1 = turtle.Turtle()
p1.shape("square")
p1.shapesize(stretch_wid=GRID_SIZE / 20, stretch_len=GRID_SIZE / 20)
p1.color("white", "#c0392b")
p1.penup()
p1.direction = "stop"
p1.is_trail_active = False

p2 = turtle.Turtle()
p2.shape("square")
p2.shapesize(stretch_wid=GRID_SIZE / 20, stretch_len=GRID_SIZE / 20)
p2.color("white", "#0865ac")
p2.penup()
p2.direction = "stop"
p2.is_trail_active = False

# ===========================================
# CONTROLS
# ===========================================
def p1_up():
    if game_state == "PLAYING" and p1.direction != "down":
        p1.direction = "up"

def p1_down():
    if game_state == "PLAYING" and p1.direction != "up":
        p1.direction = "down"

def p1_left():
    if game_state == "PLAYING" and p1.direction != "right":
        p1.direction = "left"

def p1_right():
    if game_state == "PLAYING" and p1.direction != "left":
        p1.direction = "right"

def p2_up():
    if game_state == "PLAYING" and p2.direction != "down":
        p2.direction = "up"

def p2_down():
    if game_state == "PLAYING" and p2.direction != "up":
        p2.direction = "down"

def p2_left():
    if game_state == "PLAYING" and p2.direction != "right":
        p2.direction = "left"

def p2_right():
    if game_state == "PLAYING" and p2.direction != "left":
        p2.direction = "right"

wn.listen()
wn.onkeypress(p1_up, "w")
wn.onkeypress(p1_down, "s")
wn.onkeypress(p1_left, "a")
wn.onkeypress(p1_right, "d")
wn.onkeypress(p1_up, "W")
wn.onkeypress(p1_down, "S")
wn.onkeypress(p1_left, "A")
wn.onkeypress(p1_right, "D")
wn.onkeypress(p2_up, "Up")
wn.onkeypress(p2_down, "Down")
wn.onkeypress(p2_left, "Left")
wn.onkeypress(p2_right, "Right")

# ===========================================
# COLLISION & PLAYER STEP LOGIC
# ===========================================
# Collision Mode:
# "ELIMINATION" (Default): Hitting enemy tail eliminates them (tail vanishes) & attacker wins!
# "RESPAWN": Hitting enemy tail wipes their tail (ชนหางหาย) & sends them back to base to keep playing until time ends!
COLLISION_MODE = "ELIMINATION"

def clear_trail(trail_id):
    """Wipes all cells of trail_id from the grid and removes turtle stamps (ชนหางหาย)."""
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == trail_id:
                set_cell(r, c, 0)
    render_dirty_cells()

def respawn_player(player_turtle, player_id):
    """Resets player position back to home base."""
    if player_id == 1:
        start_r, start_c = ROWS // 2, COLS // 5
    else:
        start_r, start_c = ROWS // 2, (COLS * 4) // 5
    player_turtle.goto(grid_to_screen(start_r, start_c))
    player_turtle.direction = "stop"
    player_turtle.is_trail_active = False

def trigger_game_over(winner_text, color=None):
    """Halts match, hides players, and renders Game Over with winner or draw banner."""
    global game_state
    game_state = "GAME_OVER"
    p1.hideturtle()
    p2.hideturtle()
    render_dirty_cells()
    draw_game_over(winner_text, color)

def update_game_step():
    """
    Simultaneously steps both players and evaluates all collisions:
    1. Head-on collision (ชนกันตรงๆ) -> DRAW (เสมอ) และหางหายทั้งคู่
    2. Mutual tail cut (ชนหางพร้อมกัน) -> DRAW (เสมอ) และหางหายทั้งคู่
    3. Tail cut (ชนหางฝ่ายตรงข้าม) -> หางของฝ่ายที่ถูกชนหายทันที (ชนหางหาย)
    4. Territory capture & trail expansion
    """
    global game_state

    if game_state != "PLAYING":
        return

    p1_moving = (p1.direction != "stop")
    p2_moving = (p2.direction != "stop")

    if not p1_moving and not p2_moving:
        return

    curr_r1, curr_c1 = screen_to_grid(p1.xcor(), p1.ycor())
    curr_r2, curr_c2 = screen_to_grid(p2.xcor(), p2.ycor())

    next_r1, next_c1 = curr_r1, curr_c1
    if p1.direction == "up": next_r1 -= 1
    elif p1.direction == "down": next_r1 += 1
    elif p1.direction == "left": next_c1 -= 1
    elif p1.direction == "right": next_c1 += 1

    next_r2, next_c2 = curr_r2, curr_c2
    if p2.direction == "up": next_r2 -= 1
    elif p2.direction == "down": next_r2 += 1
    elif p2.direction == "left": next_c2 -= 1
    elif p2.direction == "right": next_c2 += 1

    # Check boundaries
    p1_valid = (0 <= next_r1 < ROWS and 0 <= next_c1 < COLS)
    p2_valid = (0 <= next_r2 < ROWS and 0 <= next_c2 < COLS)

    if not p1_valid:
        next_r1, next_c1 = curr_r1, curr_c1
        p1.direction = "stop"
    if not p2_valid:
        next_r2, next_c2 = curr_r2, curr_c2
        p2.direction = "stop"

    # ---------------------------------------------------------
    # 1. HEAD-ON COLLISION (ชนประสานงา -> DRAW)
    # ---------------------------------------------------------
    same_cell = (next_r1 == next_r2 and next_c1 == next_c2) and (p1_moving or p2_moving)
    crossed_paths = (next_r1 == curr_r2 and next_c1 == curr_c2 and next_r2 == curr_r1 and next_c2 == curr_c1)

    if same_cell or crossed_paths:
        clear_trail(3)
        clear_trail(4)
        p1.is_trail_active = False
        p2.is_trail_active = False
        trigger_game_over("IT'S A DRAW! (HEAD-ON COLLISION)", "#f1c40f")
        return

    # ---------------------------------------------------------
    # 2. TAIL COLLISION (ชนหางหาย)
    # ---------------------------------------------------------
    target1 = grid[next_r1][next_c1] if (p1_moving and p1_valid) else None
    target2 = grid[next_r2][next_c2] if (p2_moving and p2_valid) else None

    p1_cuts_p2 = (target1 == 4)  # P1 hits P2's tail
    p2_cuts_p1 = (target2 == 3)  # P2 hits P1's tail

    if p1_cuts_p2 and p2_cuts_p1:
        # Both hit each other's tail in the same frame -> DRAW
        clear_trail(3)
        clear_trail(4)
        p1.is_trail_active = False
        p2.is_trail_active = False
        trigger_game_over("IT'S A DRAW! (MUTUAL TAIL CUT)", "#f1c40f")
        return

    if p1_cuts_p2:
        # P1 cuts P2's tail -> P2's tail disappears!
        clear_trail(4)
        p2.is_trail_active = False
        if COLLISION_MODE == "ELIMINATION":
            trigger_game_over("PLAYER 1 (RED) WINS! (TAIL CUT)", "#e74c3c")
            return
        else:
            respawn_player(p2, 2)

    if p2_cuts_p1:
        # P2 cuts P1's tail -> P1's tail disappears!
        clear_trail(3)
        p1.is_trail_active = False
        if COLLISION_MODE == "ELIMINATION":
            trigger_game_over("PLAYER 2 (BLUE) WINS! (TAIL CUT)", "#0984e3")
            return
        else:
            respawn_player(p1, 1)

    # ---------------------------------------------------------
    # 3. MOVEMENT & TERRITORY CONQUEST
    # ---------------------------------------------------------
    if p1_moving and p1_valid:
        p1.goto(grid_to_screen(next_r1, next_c1))
        t1 = grid[next_r1][next_c1]
        if t1 == 1:
            if getattr(p1, "is_trail_active", False):
                close_loop_and_fill(1, 3)
                p1.is_trail_active = False
        elif t1 == 3:
            close_loop_and_fill(1, 3)
            p1.is_trail_active = False
        else:
            set_cell(next_r1, next_c1, 3)
            p1.is_trail_active = True

    if p2_moving and p2_valid:
        p2.goto(grid_to_screen(next_r2, next_c2))
        t2 = grid[next_r2][next_c2]
        if t2 == 2:
            if getattr(p2, "is_trail_active", False):
                close_loop_and_fill(2, 4)
                p2.is_trail_active = False
        elif t2 == 4:
            close_loop_and_fill(2, 4)
            p2.is_trail_active = False
        else:
            set_cell(next_r2, next_c2, 4)
            p2.is_trail_active = True

# ===========================================
# UI & MENU DRAWING FUNCTIONS
# ===========================================
def draw_button(x, y, w, h, text, bg_color, text_color="white"):
    """Draws a UI button with specified dimensions and colors."""
    pen.goto(x - w / 2, y - h / 2)
    pen.color(bg_color)
    pen.begin_fill()

    for _ in range(2):
        pen.forward(w)
        pen.left(90)
        pen.forward(h)
        pen.left(90)

    pen.end_fill()
    pen.goto(x, y - 10)
    pen.color(text_color)
    pen.write(text, align="center", font=("Courier", 14, "bold"))

def draw_menu():
    """Renders Main Menu Screen."""
    pen.clear()

    # Title
    pen.goto(0, 160)
    pen.color("#f1c40f")
    pen.write("DON'T TOUCH MY AREA", align="center", font=("Courier", 26, "bold"))

    # Controls Info
    pen.goto(-150, 80)
    pen.color("#e74c3c")
    pen.write("PLAYER 1 (Red)\nWASD Keys", align="center", font=("Courier", 13, "bold"))

    pen.goto(150, 80)
    pen.color("#0984e3")
    pen.write("PLAYER 2 (Blue)\nArrow Keys", align="center", font=("Courier", 13, "bold"))

    # Time Selector Header
    pen.goto(0, -10)
    pen.color("white")
    pen.write("SELECT MATCH DURATION", align="center", font=("Courier", 14, "bold"))

    # 10s, 30s, 60s Buttons
    times = [10, 30, 60]
    x_pos = [-120, 0, 120]

    for t, x in zip(times, x_pos):
        color = "#2ecc71" if t == selected_time else "#34495e"
        draw_button(x, -50, 80, 40, f"{t}s", color)

    # Start Game Button
    draw_button(0, -130, 180, 50, "START GAME", "#e74c3c")

def draw_game_over(winner_text=None, color=None):
    """Renders Game Over Screen with results and Play Again button."""
    pen.clear()

    p1_tiles = sum(row.count(1) for row in grid)
    p2_tiles = sum(row.count(2) for row in grid)

    if winner_text is None:
        if p1_tiles > p2_tiles:
            winner_text = "PLAYER 1 (RED) WINS!"
            color = "#e74c3c"
        elif p2_tiles > p1_tiles:
            winner_text = "PLAYER 2 (BLUE) WINS!"
            color = "#0984e3"
        else:
            winner_text = "IT'S A DRAW!"
            color = "#f1c40f"
    elif color is None:
        if "DRAW" in winner_text:
            color = "#f1c40f"
        elif "1" in winner_text or "RED" in winner_text:
            color = "#e74c3c"
        else:
            color = "#0984e3"

    pen.goto(0, 80)
    pen.color(color)
    pen.write(winner_text, align="center", font=("Courier", 20, "bold"))

    p1_pct = (p1_tiles / TOTAL_CELLS) * 100
    p2_pct = (p2_tiles / TOTAL_CELLS) * 100

    pen.goto(0, 20)
    pen.color("white")
    pen.write(
        f"P1: {p1_tiles} ({p1_pct:.1f}%) | P2: {p2_tiles} ({p2_pct:.1f}%)",
        align="center",
        font=("Courier", 15, "bold")
    )

    # Play Again Button
    draw_button(0, -60, 180, 50, "PLAY AGAIN", "#2ecc71")

def update_hud():
    """Updates Scoreboard and Countdown Timer during gameplay."""
    global game_state, time_left

    if game_state != "PLAYING":
        return

    elapsed = time.time() - start_time_stamp
    time_left = max(0, int(selected_time - elapsed))

    p1_tiles = sum(row.count(1) for row in grid)
    p2_tiles = sum(row.count(2) for row in grid)

    pen.clear()
    pen.goto(0, (SCREEN_SIZE / 2) + 12)
    timer_color = "#e74c3c" if time_left <= 5 else "white"
    pen.color(timer_color)
    pen.write(
        f"P1: {p1_tiles} pts | TIME: {time_left}s | P2: {p2_tiles} pts",
        align="center",
        font=("Courier", 13, "bold")
    )

    if time_left <= 0:
        trigger_game_over(None, None)

def reset_game():
    """Resets grid and player states for a new match."""
    global grid, dirty_cells, tile_stamps

    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    dirty_cells.clear()
    stamper.clearstamps()
    tile_stamps.clear()

    # Reset Players
    p1_start_r, p1_start_c = ROWS // 2, COLS // 5
    p1.goto(grid_to_screen(p1_start_r, p1_start_c))
    p1.direction = "stop"
    p1.is_trail_active = False
    p1.showturtle()

    p2_start_r, p2_start_c = ROWS // 2, (COLS * 4) // 5
    p2.goto(grid_to_screen(p2_start_r, p2_start_c))
    p2.direction = "stop"
    p2.is_trail_active = False
    p2.showturtle()

    # Spawn initial territory bases (5x5 tiles for comfortable control on 100x100 grid)
    BASE_RADIUS = 2
    for dr in range(-BASE_RADIUS, BASE_RADIUS + 1):
        for dc in range(-BASE_RADIUS, BASE_RADIUS + 1):
            set_cell(p1_start_r + dr, p1_start_c + dc, 1)
            set_cell(p2_start_r + dr, p2_start_c + dc, 2)

    render_dirty_cells()

# ===========================================
# MOUSE CLICK HANDLER
# ===========================================
def handle_click(x, y):
    global game_state, selected_time, start_time_stamp

    if game_state == "MENU":
        # Check 10s button (-160 <= x <= -80, -70 <= y <= -30)
        if -160 <= x <= -80 and -70 <= y <= -30:
            selected_time = 10
            draw_menu()

        # Check 30s button (-40 <= x <= 40, -70 <= y <= -30)
        elif -40 <= x <= 40 and -70 <= y <= -30:
            selected_time = 30
            draw_menu()

        # Check 60s button (80 <= x <= 160, -70 <= y <= -30)
        elif 80 <= x <= 160 and -70 <= y <= -30:
            selected_time = 60
            draw_menu()

        # Check Start button (-90 <= x <= 90, -155 <= y <= -105)
        elif -90 <= x <= 90 and -155 <= y <= -105:
            pen.clear()
            reset_game()
            start_time_stamp = time.time()
            game_state = "PLAYING"

    elif game_state == "GAME_OVER":
        # Check Play Again button (-90 <= x <= 90, -85 <= y <= -35)
        if -90 <= x <= 90 and -85 <= y <= -35:
            clear_trail(3)
            clear_trail(4)
            stamper.clearstamps()
            game_state = "MENU"
            draw_menu()

wn.onscreenclick(handle_click)

# ===========================================
# INITIAL HUD DRAW & GAME LOOP
# ===========================================
draw_menu()

def game_loop():
    if game_state == "PLAYING":
        update_game_step()
        render_dirty_cells()
        update_hud()

    try:
        wn.update()
        wn.ontimer(game_loop, 30)
    except (turtle.Terminator, Exception):
        pass

game_loop()
wn.mainloop()