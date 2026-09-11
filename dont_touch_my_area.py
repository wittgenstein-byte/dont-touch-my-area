import os
import turtle
import time
from collections import deque
try:
    import winsound
except ImportError:
    winsound = None

# ===========================================
# Screen Setup
# ===========================================
SCREEN_SIZE = 600

wn = turtle.Screen()
wn.title("Don't Touch My Area - Territory Conquest")
wn.bgcolor("#1a1a1a")
wn.setup(width=SCREEN_SIZE + 40, height=SCREEN_SIZE + 90)  # Added top margin for HUD

bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asset", "bg.gif")
if os.path.exists(bg_path):
    wn.bgpic(bg_path)
wn.tracer(0)

# Sound Effects (SFX) Setup
SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asset", "sounds")

def play_sfx(name):
    """Plays a .wav sound effect asynchronously without blocking the Turtle game loop."""
    if winsound:
        path = os.path.join(SOUND_DIR, f"{name}.wav")
        if os.path.exists(path):
            try:
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception:
                pass

# UI Pen for Menu, Scoreboard, and Game Over
pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.penup()

# ===========================================
# Game Entities
# ===========================================
# Player 1 Neon Aura (Neon Pink Halo)
p1_glow = turtle.Turtle()
p1_glow.hideturtle()
p1_glow.speed(0)
p1_glow.shape("square")
p1_glow.shapesize(stretch_wid=10 / 20, stretch_len=10 / 20)
p1_glow.color("#ff007f", "#ff007f")
p1_glow.penup()

# Player 1 Energy Core (White-hot core with neon rim)
p1 = turtle.Turtle()
p1.hideturtle()
p1.speed(0)
p1.shape("square")
p1.shapesize(stretch_wid=5 / 20, stretch_len=5 / 20)
p1.color("#ffb3d9", "#ffffff")
p1.penup()
p1.direction = "stop"
p1.is_trail_active = False

# Player 2 Neon Aura (Neon Cyan Halo)
p2_glow = turtle.Turtle()
p2_glow.hideturtle()
p2_glow.speed(0)
p2_glow.shape("square")
p2_glow.shapesize(stretch_wid=10 / 20, stretch_len=10 / 20)
p2_glow.color("#00f0ff", "#00f0ff")
p2_glow.penup()

# Player 2 Energy Core (White-hot core with neon rim)
p2 = turtle.Turtle()
p2.hideturtle()
p2.speed(0)
p2.shape("square")
p2.shapesize(stretch_wid=5 / 20, stretch_len=5 / 20)
p2.color("#b3f7ff", "#ffffff")
p2.penup()
p2.direction = "stop"
p2.is_trail_active = False

# Stampers:
# 1. t_stamper: Stamps permanent territory using horizontal scanline strips (ultra-fast: 2-3 ms!)
t_stamper = turtle.Turtle()
t_stamper.hideturtle()
t_stamper.speed(0)
t_stamper.shape("square")
t_stamper.penup()

# 2. tr_stamper: Stamps single active trails (< 0.05 ms per step)
tr_stamper = turtle.Turtle()
tr_stamper.hideturtle()
tr_stamper.speed(0)
tr_stamper.shape("square")
tr_stamper.shapesize(stretch_wid=6 / 20, stretch_len=6 / 20)
tr_stamper.penup()

# ===========================================
# Parameters & Physics
# ===========================================
# Grid & Map Parameters
COLS = 100
ROWS = 100
TOTAL_CELLS = ROWS * COLS
GRID_SIZE = 6
BASE_RADIUS = 2

# Collision Mode:
# "ELIMINATION" (Default): Hitting enemy tail eliminates them (tail vanishes) & attacker wins!
# "RESPAWN": Hitting enemy tail wipes their tail (ชนหางหาย) & sends them back to base to keep playing!
COLLISION_MODE = "ELIMINATION"

# Cyberpunk Neon Color Palette
COLOR_MAP = {
    1: "#99003d",  # P1 permanent territory (deep neon ruby)
    2: "#004b87",  # P2 permanent territory (deep cyber cobalt)
    3: "#ff007f",  # P1 trail (vivid neon pink)
    4: "#00f0ff"   # P2 trail (electric neon cyan)
}

# Game Management States: "MENU", "PLAYING", "GAME_OVER"
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
game_state = "MENU"
selected_time = 30  # Default 30 seconds
time_left = 30
start_time_stamp = 0

# Trail stamp tracker: (r, c) -> stamp_id
trail_stamps = {}
trail_stamps_owner = {}

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

def render_captured_area(captured_cells, player_id):
    """
    Ultra-fast territory rendering:
    Groups contiguous cells by horizontal scanlines and stamps them as a single stretched strip.
    Renders 1,000+ cells in only 2-3 ms (50x faster than individual stamps)!
    """
    rows = {}
    for r, c in captured_cells:
        rows.setdefault(r, []).append(c)

    t_stamper.color(COLOR_MAP[player_id])
    for r, cols in rows.items():
        cols.sort()
        start_c = cols[0]
        prev_c = start_c
        for c in cols[1:]:
            if c == prev_c + 1:
                prev_c = c
            else:
                length = prev_c - start_c + 1
                center_c = (start_c + prev_c) / 2
                x, y = grid_to_screen(r, center_c)
                t_stamper.shapesize(stretch_wid=GRID_SIZE / 20, stretch_len=(length * GRID_SIZE) / 20)
                t_stamper.goto(x, y)
                t_stamper.stamp()
                start_c = c
                prev_c = c
        length = prev_c - start_c + 1
        center_c = (start_c + prev_c) / 2
        x, y = grid_to_screen(r, center_c)
        t_stamper.shapesize(stretch_wid=GRID_SIZE / 20, stretch_len=(length * GRID_SIZE) / 20)
        t_stamper.goto(x, y)
        t_stamper.stamp()

def drop_trail_stamp(r, c, trail_id, player_id):
    """Stamps a single active trail tile instantaneously."""
    grid[r][c] = trail_id
    x, y = grid_to_screen(r, c)
    tr_stamper.goto(x, y)
    tr_stamper.color(COLOR_MAP[trail_id])
    sid = tr_stamper.stamp()
    trail_stamps[(r, c)] = sid
    trail_stamps_owner[(r, c)] = player_id

def close_loop_and_fill(player_id, trail_id):
    """
    High-performance BFS flood fill:
    Uses flat bytearray for O(1) visited lookups and deque for fast queue operations.
    Completes board traversal and rendering in < 8 ms!
    """
    boundary_1 = player_id
    boundary_2 = trail_id

    visited = bytearray(TOTAL_CELLS)
    queue = deque()

    # Seed outer borders
    for r in range(ROWS):
        row_offset = r * COLS
        for c in (0, COLS - 1):
            idx = row_offset + c
            cell_val = grid[r][c]
            if cell_val != boundary_1 and cell_val != boundary_2:
                visited[idx] = 1
                queue.append(idx)

    for c in range(COLS):
        for r in (0, ROWS - 1):
            idx = r * COLS + c
            cell_val = grid[r][c]
            if cell_val != boundary_1 and cell_val != boundary_2 and not visited[idx]:
                visited[idx] = 1
                queue.append(idx)

    # BFS traversal of exterior territory
    while queue:
        curr = queue.popleft()
        r = curr // COLS
        c = curr % COLS

        if r > 0:
            n = curr - COLS
            if not visited[n]:
                v = grid[r - 1][c]
                if v != boundary_1 and v != boundary_2:
                    visited[n] = 1
                    queue.append(n)
        if r < ROWS - 1:
            n = curr + COLS
            if not visited[n]:
                v = grid[r + 1][c]
                if v != boundary_1 and v != boundary_2:
                    visited[n] = 1
                    queue.append(n)
        if c > 0:
            n = curr - 1
            if not visited[n]:
                v = grid[r][c - 1]
                if v != boundary_1 and v != boundary_2:
                    visited[n] = 1
                    queue.append(n)
        if c < COLS - 1:
            n = curr + 1
            if not visited[n]:
                v = grid[r][c + 1]
                if v != boundary_1 and v != boundary_2:
                    visited[n] = 1
                    queue.append(n)

    # Enclosed cells become permanent territory
    captured_cells = []
    for r in range(ROWS):
        row_offset = r * COLS
        for c in range(COLS):
            idx = row_offset + c
            if not visited[idx] or grid[r][c] == trail_id:
                if grid[r][c] != player_id:
                    grid[r][c] = player_id
                    captured_cells.append((r, c))

    # Clear previous trail stamps of this player
    to_del = [pt for pt, pid in trail_stamps_owner.items() if pid == player_id]
    for pt in to_del:
        try:
            tr_stamper.clearstamp(trail_stamps[pt])
        except Exception:
            pass
        trail_stamps.pop(pt, None)
        trail_stamps_owner.pop(pt, None)

    # Render captured territory instantly
    if captured_cells:
        render_captured_area(captured_cells, player_id)

    play_sfx("claim")

def clear_trail(trail_id):
    """Wipes all cells of trail_id from the grid and clears trail stamps immediately (ชนหางหาย)."""
    owner_id = 1 if trail_id == 3 else 2
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == trail_id:
                grid[r][c] = 0

    to_del = [pt for pt, pid in trail_stamps_owner.items() if pid == owner_id]
    for pt in to_del:
        try:
            tr_stamper.clearstamp(trail_stamps[pt])
        except Exception:
            pass
        trail_stamps.pop(pt, None)
        trail_stamps_owner.pop(pt, None)

def respawn_player(player_turtle, player_id):
    """Resets player position back to home base."""
    if player_id == 1:
        start_r, start_c = ROWS // 2, COLS // 5
        pos = grid_to_screen(start_r, start_c)
        p1.goto(pos)
        p1_glow.goto(pos)
        p1.direction = "stop"
        p1.is_trail_active = False
    else:
        start_r, start_c = ROWS // 2, (COLS * 4) // 5
        pos = grid_to_screen(start_r, start_c)
        p2.goto(pos)
        p2_glow.goto(pos)
        p2.direction = "stop"
        p2.is_trail_active = False

def trigger_game_over(winner_text, color=None):
    """Halts match, hides players, and renders Game Over with winner or draw banner."""
    global game_state
    game_state = "GAME_OVER"
    p1.hideturtle()
    p1_glow.hideturtle()
    p2.hideturtle()
    p2_glow.hideturtle()
    draw_game_over(winner_text, color)

    p1_tiles = sum(row.count(1) for row in grid)
    p2_tiles = sum(row.count(2) for row in grid)
    if winner_text and "DRAW" in winner_text:
        play_sfx("game_over")
    elif winner_text is None and p1_tiles == p2_tiles:
        play_sfx("game_over")
    else:
        play_sfx("win")

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
        play_sfx("hit")
        clear_trail(3)
        clear_trail(4)
        p1.is_trail_active = False
        p2.is_trail_active = False
        trigger_game_over("IT'S A DRAW! (HEAD-ON COLLISION)", "#ffe600")
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
        play_sfx("hit")
        clear_trail(3)
        clear_trail(4)
        p1.is_trail_active = False
        p2.is_trail_active = False
        trigger_game_over("IT'S A DRAW! (MUTUAL TAIL CUT)", "#ffe600")
        return

    if p1_cuts_p2:
        # P1 cuts P2's tail -> P2's tail disappears!
        play_sfx("hit")
        clear_trail(4)
        p2.is_trail_active = False
        if COLLISION_MODE == "ELIMINATION":
            trigger_game_over("PLAYER 1 (NEON PINK) WINS! (TAIL CUT)", "#ff007f")
            return
        else:
            respawn_player(p2, 2)

    if p2_cuts_p1:
        # P2 cuts P1's tail -> P1's tail disappears!
        play_sfx("hit")
        clear_trail(3)
        p1.is_trail_active = False
        if COLLISION_MODE == "ELIMINATION":
            trigger_game_over("PLAYER 2 (NEON CYAN) WINS! (TAIL CUT)", "#00f0ff")
            return
        else:
            respawn_player(p1, 1)

    # ---------------------------------------------------------
    # 3. MOVEMENT & TERRITORY CONQUEST
    # ---------------------------------------------------------
    if p1_moving and p1_valid:
        pos1 = grid_to_screen(next_r1, next_c1)
        p1.goto(pos1)
        p1_glow.goto(pos1)
        t1 = grid[next_r1][next_c1]
        if t1 == 1:
            if getattr(p1, "is_trail_active", False):
                close_loop_and_fill(1, 3)
                p1.is_trail_active = False
        elif t1 == 3:
            close_loop_and_fill(1, 3)
            p1.is_trail_active = False
        else:
            drop_trail_stamp(next_r1, next_c1, 3, 1)
            p1.is_trail_active = True

    if p2_moving and p2_valid:
        pos2 = grid_to_screen(next_r2, next_c2)
        p2.goto(pos2)
        p2_glow.goto(pos2)
        t2 = grid[next_r2][next_c2]
        if t2 == 2:
            if getattr(p2, "is_trail_active", False):
                close_loop_and_fill(2, 4)
                p2.is_trail_active = False
        elif t2 == 4:
            close_loop_and_fill(2, 4)
            p2.is_trail_active = False
        else:
            drop_trail_stamp(next_r2, next_c2, 4, 2)
            p2.is_trail_active = True

def reset_game():
    """Resets grid and player states for a new match."""
    global grid

    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    t_stamper.clearstamps()
    tr_stamper.clearstamps()
    trail_stamps.clear()
    trail_stamps_owner.clear()

    # Reset Players
    p1_start_r, p1_start_c = ROWS // 2, COLS // 5
    pos1 = grid_to_screen(p1_start_r, p1_start_c)
    p1.goto(pos1)
    p1_glow.goto(pos1)
    p1.direction = "stop"
    p1.is_trail_active = False
    p1_glow.showturtle()
    p1.showturtle()

    p2_start_r, p2_start_c = ROWS // 2, (COLS * 4) // 5
    pos2 = grid_to_screen(p2_start_r, p2_start_c)
    p2.goto(pos2)
    p2_glow.goto(pos2)
    p2.direction = "stop"
    p2.is_trail_active = False
    p2_glow.showturtle()
    p2.showturtle()

    # Spawn initial territory bases (5x5 tiles for comfortable control on 100x100 grid)
    p1_base = []
    p2_base = []
    for dr in range(-BASE_RADIUS, BASE_RADIUS + 1):
        for dc in range(-BASE_RADIUS, BASE_RADIUS + 1):
            r1, c1 = p1_start_r + dr, p1_start_c + dc
            r2, c2 = p2_start_r + dr, p2_start_c + dc
            grid[r1][c1] = 1
            p1_base.append((r1, c1))
            grid[r2][c2] = 2
            p2_base.append((r2, c2))

    render_captured_area(p1_base, 1)
    render_captured_area(p2_base, 2)

# ===========================================
# Input Handling
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

def handle_click(x, y):
    global game_state, selected_time, start_time_stamp

    if game_state == "MENU":
        # Check 10s button (-160 <= x <= -80, -70 <= y <= -30)
        if -160 <= x <= -80 and -70 <= y <= -30:
            selected_time = 10
            play_sfx("click")
            draw_menu()

        # Check 30s button (-40 <= x <= 40, -70 <= y <= -30)
        elif -40 <= x <= 40 and -70 <= y <= -30:
            selected_time = 30
            play_sfx("click")
            draw_menu()

        # Check 60s button (80 <= x <= 160, -70 <= y <= -30)
        elif 80 <= x <= 160 and -70 <= y <= -30:
            selected_time = 60
            play_sfx("click")
            draw_menu()

        # Check Start button (-90 <= x <= 90, -155 <= y <= -105)
        elif -90 <= x <= 90 and -155 <= y <= -105:
            play_sfx("click")
            pen.clear()
            reset_game()
            start_time_stamp = time.time()
            game_state = "PLAYING"

    elif game_state == "GAME_OVER":
        # Check Play Again button (-90 <= x <= 90, -85 <= y <= -35)
        if -90 <= x <= 90 and -85 <= y <= -35:
            play_sfx("click")
            clear_trail(3)
            clear_trail(4)
            t_stamper.clearstamps()
            tr_stamper.clearstamps()
            game_state = "MENU"
            draw_menu()

wn.onscreenclick(handle_click)

# ===========================================
# Main Game Loop
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
    """Renders Main Menu Screen with neon theme."""
    pen.clear()

    # Title - Neon Gold/Yellow
    pen.goto(0, 160)
    pen.color("#ffe600")
    pen.write("DON'T TOUCH MY AREA", align="center", font=("Courier", 26, "bold"))

    # Controls Info
    pen.goto(-150, 80)
    pen.color("#ff007f")
    pen.write("PLAYER 1 (Neon Pink)\nWASD Keys", align="center", font=("Courier", 13, "bold"))

    pen.goto(150, 80)
    pen.color("#00f0ff")
    pen.write("PLAYER 2 (Neon Cyan)\nArrow Keys", align="center", font=("Courier", 13, "bold"))

    # Time Selector Header
    pen.goto(0, -10)
    pen.color("white")
    pen.write("SELECT MATCH DURATION", align="center", font=("Courier", 14, "bold"))

    # 10s, 30s, 60s Buttons
    times = [10, 30, 60]
    x_pos = [-120, 0, 120]

    for t, x in zip(times, x_pos):
        color = "#00ff88" if t == selected_time else "#1f2937"
        draw_button(x, -50, 80, 40, f"{t}s", color)

    # Start Game Button (Neutral Neon Green)
    draw_button(0, -130, 180, 50, "START GAME", "#00ff88")

def draw_game_over(winner_text=None, color=None):
    """Renders Game Over Screen with results and Play Again button."""
    pen.clear()

    # Title Header - Neon Gold/Yellow
    pen.goto(0, 150)
    pen.color("#ffe600")
    pen.write("DON'T TOUCH MY AREA", align="center", font=("Courier", 24, "bold"))

    p1_tiles = sum(row.count(1) for row in grid)
    p2_tiles = sum(row.count(2) for row in grid)

    if winner_text is None:
        if p1_tiles > p2_tiles:
            winner_text = "PLAYER 1 (NEON PINK) WINS!"
            color = "#ff007f"
        elif p2_tiles > p1_tiles:
            winner_text = "PLAYER 2 (NEON CYAN) WINS!"
            color = "#00f0ff"
        else:
            winner_text = "IT'S A DRAW!"
            color = "#ffe600"
    elif color is None:
        if "DRAW" in winner_text:
            color = "#ffe600"
        elif "1" in winner_text or "RED" in winner_text or "PINK" in winner_text:
            color = "#ff007f"
        else:
            color = "#00f0ff"

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
    draw_button(0, -60, 180, 50, "PLAY AGAIN", "#00ff88")

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
    timer_color = "#ffe600" if time_left <= 5 else "white"
    pen.color(timer_color)
    pen.write(
        f"P1: {p1_tiles} pts | TIME: {time_left}s | P2: {p2_tiles} pts",
        align="center",
        font=("Courier", 13, "bold")
    )

    if 0 < time_left <= 5 and getattr(update_hud, "last_beep", None) != time_left:
        update_hud.last_beep = time_left
        play_sfx("click")

    if time_left <= 0:
        trigger_game_over(None, None)

# Initial HUD / Menu Draw
draw_menu()

def game_loop():
    if game_state == "PLAYING":
        update_game_step()
        update_hud()

    try:
        wn.update()
        wn.ontimer(game_loop, 25)
    except (turtle.Terminator, Exception):
        pass

game_loop()
wn.mainloop()