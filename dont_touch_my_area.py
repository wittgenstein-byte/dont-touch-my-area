"""
=============================================================================
DON'T TOUCH MY AREA - TERRITORY CONQUEST (CYBERPUNK NEON EDITION)
=============================================================================
2-Player Territory Conquest game built with Python Turtle.
- Grid Resolution: 100 x 100 Tiles (10,000 total cells) scaled to 600x600 px arena
- Core Mechanics: Draw trails to capture territory (BFS Inverted Flood Fill),
  tail-cut elimination ("ชนหางหาย"), and head-on collision draws.
- Baseline Architecture Structure:
  1. # Screen Setup
  2. # Game Entities
  3. # Parameters & Physics
  4. # Input Handling
  5. # Main Game Loop
=============================================================================
"""

import os
import turtle
import time
from collections import deque

# Load Windows audio modules (ctypes for looping BGM, winsound for concurrent SFX)
try:
    import ctypes                        # Windows C-types library for MCI background music playback
    import winsound                      # Import Windows audio module for low-latency sound effects
except ImportError:
    ctypes = None
    winsound = None                      # Graceful fallback if running on non-Windows environment

# =============================================================================
# Screen Setup
# =============================================================================
SCREEN_SIZE = 600                        # Playable arena size in pixels (600x600 px)

# 1. Window Initialization
wn = turtle.Screen()                     # Instantiate Screen object for window management
wn.title("Don't Touch My Area - Territory Conquest")  # Set window title bar text
wn.bgcolor("#1a1a1a")                    # Set background color to dark cyberpunk gray
wn.setup(width=SCREEN_SIZE + 40, height=SCREEN_SIZE + 90)  # Set window resolution (640x690 px)

# Load custom background image if asset exists
bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asset", "bg.gif")  # Get asset path
if os.path.exists(bg_path):              # Verify background file exists on disk
    wn.bgpic(bg_path)                    # Apply background image to game screen

wn.tracer(0)                             # Turn off auto-screen update for manual frame control (prevents lag)

# 2. Audio Engine (BGM & Sound Effects)
SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asset", "sounds")  # Sound folder path
current_bgm = None                       # Track currently active background music track

def play_bgm(track):
    """Play background music track ('lobby' or 'playing') in a seamless loop using Windows MCI."""
    global current_bgm
    if current_bgm == track:             # Avoid restarting track if already playing
        return
    current_bgm = track                  # Update active BGM track identifier
    if not ctypes:                       # Verify ctypes availability
        return
    try:
        ctypes.windll.winmm.mciSendStringW("close bgm", None, 0, None)  # Close previous audio device
        # Look for possible file variations (e.g., LobbyMusic.wav, lobby.wav, PlayingMusic.wav, playing.wav)
        candidates = [
            f"{track}.wav",
            f"{track.capitalize()}.wav",
            f"{track.capitalize()}Music.wav",
            f"{track}Music.wav"
        ]
        target_path = None
        for cand in candidates:
            cand_path = os.path.join(SOUND_DIR, cand)
            if os.path.exists(cand_path):
                target_path = cand_path
                break
        if target_path:
            short_buf = ctypes.create_unicode_buffer(260)  # Buffer for 8.3 short path name required by MCI
            ctypes.windll.kernel32.GetShortPathNameW(os.path.abspath(target_path), short_buf, 260)
            sp = short_buf.value         # Retrieve safe short path string
            ctypes.windll.winmm.mciSendStringW(f'open {sp} type mpegvideo alias bgm', None, 0, None)  # Open device
            ctypes.windll.winmm.mciSendStringW('play bgm repeat', None, 0, None)  # Play track in continuous loop
    except Exception:
        pass                             # Suppress any media subsystem exceptions silently

def stop_bgm():
    """Stop and close background music playback."""
    global current_bgm
    current_bgm = None                   # Reset active track identifier
    if ctypes:
        try:
            ctypes.windll.winmm.mciSendStringW("close bgm", None, 0, None)  # Close and release MCI audio device
        except Exception:
            pass                         # Suppress exceptions

def play_sfx(name):
    """Play a sound effect asynchronously without interrupting game execution."""
    if winsound:                         # Check if winsound module is available on Windows
        path = os.path.join(SOUND_DIR, f"{name}.wav")  # Construct full path to target WAV sound file
        if os.path.exists(path):         # Ensure sound file exists before playing
            try:
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)  # Play sound asynchronously
            except Exception:
                pass                     # Suppress any audio driver exceptions silently

# 3. UI and Text Rendering Pen
pen = turtle.Turtle()                    # Instantiate Turtle object for drawing UI text and buttons
pen.hideturtle()                         # Hide cursor graphics for clean presentation
pen.speed(0)                             # Set maximum animation speed for instant drawing
pen.penup()                              # Lift pen to prevent drawing default lines

# =============================================================================
# Game Entities
# =============================================================================

# --- PLAYER 1 (Neon Pink Light Cycle) ---
# Outer Neon Glow Aura
p1_glow = turtle.Turtle()                # Instantiate Turtle object for Player 1 glowing aura
p1_glow.hideturtle()                     # Hide cursor until game match starts
p1_glow.speed(0)                         # Set maximum drawing speed
p1_glow.shape("square")                  # Set aura shape to square
p1_glow.shapesize(stretch_wid=10 / 20, stretch_len=10 / 20)  # Scale aura halo size to 10x10 pixels
p1_glow.color("#ff007f", "#ff007f")      # Set outer glow aura color to vivid Neon Pink
p1_glow.penup()                          # Lift pen to move freely without drawing trails

# Inner Core Entity
p1 = turtle.Turtle()                     # Instantiate Turtle object for Player 1 main core
p1.hideturtle()                          # Hide cursor until match starts
p1.speed(0)                              # Set maximum drawing speed
p1.shape("square")                       # Set core shape to square
p1.shapesize(stretch_wid=5 / 20, stretch_len=5 / 20)  # Scale core size to 5x5 pixels
p1.color("#ffb3d9", "#ffffff")           # Set white-hot inner core with pink border
p1.penup()                               # Lift pen so player moves cleanly
p1.direction = "stop"                    # Initial movement direction ('up', 'down', 'left', 'right', 'stop')
p1.is_trail_active = False               # Flag indicating whether player is currently drawing a trail

# --- PLAYER 2 (Neon Cyan Light Cycle) ---
# Outer Neon Glow Aura
p2_glow = turtle.Turtle()                # Instantiate Turtle object for Player 2 glowing aura
p2_glow.hideturtle()                     # Hide cursor until game match starts
p2_glow.speed(0)                         # Set maximum drawing speed
p2_glow.shape("square")                  # Set aura shape to square
p2_glow.shapesize(stretch_wid=10 / 20, stretch_len=10 / 20)  # Scale aura halo size to 10x10 pixels
p2_glow.color("#00f0ff", "#00f0ff")      # Set outer glow aura color to electric Neon Cyan
p2_glow.penup()                          # Lift pen to move freely without drawing trails

# Inner Core Entity
p2 = turtle.Turtle()                     # Instantiate Turtle object for Player 2 main core
p2.hideturtle()                          # Hide cursor until match starts
p2.speed(0)                              # Set maximum drawing speed
p2.shape("square")                       # Set core shape to square
p2.shapesize(stretch_wid=5 / 20, stretch_len=5 / 20)  # Scale core size to 5x5 pixels
p2.color("#b3f7ff", "#ffffff")           # Set white-hot inner core with cyan border
p2.penup()                               # Lift pen so player moves cleanly
p2.direction = "stop"                    # Initial movement direction ('up', 'down', 'left', 'right', 'stop')
p2.is_trail_active = False               # Flag indicating whether player is currently drawing a trail

# --- HIGH-PERFORMANCE STAMPERS ---
# Fast Territory Stamper (Horizontal Scanline Run-Length)
t_stamper = turtle.Turtle()              # Instantiate Turtle object for stamping captured territory
t_stamper.hideturtle()                   # Hide cursor graphics
t_stamper.speed(0)                       # Set maximum stamping speed
t_stamper.shape("square")                # Set stamp shape to square
t_stamper.penup()                        # Lift pen so stamper jumps directly between coordinates

# Fast Trail Stamper (Single-cell trail stamping)
tr_stamper = turtle.Turtle()             # Instantiate Turtle object for stamping active trails
tr_stamper.hideturtle()                  # Hide cursor graphics
tr_stamper.speed(0)                      # Set maximum stamping speed
tr_stamper.shape("square")               # Set stamp shape to square
tr_stamper.shapesize(stretch_wid=6 / 20, stretch_len=6 / 20)  # Scale stamp to exact tile dimensions (6x6 px)
tr_stamper.penup()                       # Lift pen to jump directly between cells

# =============================================================================
# Parameters & Physics
# =============================================================================

# 1. Grid & Dimension Constants
COLS = 100                               # Total columns in playable matrix (100 columns)
ROWS = 100                               # Total rows in playable matrix (100 rows)
TOTAL_CELLS = ROWS * COLS                # Total playable grid cells (10,000 cells)
GRID_SIZE = 6                            # Pixel dimension per tile: 100 * 6 = 600 px (exact fit)
BASE_RADIUS = 2                          # Starting territory radius: 5x5 area (-2 to +2 = 25 cells)

# Collision Rule Mode:
# "ELIMINATION" (Default): Cutting enemy tail immediately wins the match
# "RESPAWN": Cutting enemy tail deletes their tail and respawns them at base
COLLISION_MODE = "ELIMINATION"           # Active collision gameplay rule

# Cyberpunk Neon Color Palette
COLOR_MAP = {
    1: "#99003d",                        # P1 Base: Deep ruby neon red territory
    2: "#004b87",                        # P2 Base: Deep cobalt cyber blue territory
    3: "#ff007f",                        # P1 Trail: Vivid neon pink light line
    4: "#00f0ff"                         # P2 Trail: Vivid electric cyan light line
}

# 2. Game State Variables
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]  # 2D grid matrix: 0=Empty, 1=P1, 2=P2, 3=P1 Trail, 4=P2 Trail
game_state = "MENU"                      # Current game scene state: "MENU", "PLAYING", "GAME_OVER"
selected_time = 30                       # Match duration selected in menu (10s, 30s, or 60s)
time_left = 30                           # Remaining match countdown time in seconds
start_time_stamp = 0                     # High-resolution start timestamp recorded with time.time()

# Trail Stamp Tracking Dictionaries
trail_stamps = {}                        # Map grid coordinate (r, c) -> Turtle stamp ID
trail_stamps_owner = {}                  # Map grid coordinate (r, c) -> Player ID (1 or 2)

# 3. Coordinate Transformation Physics
def screen_to_grid(x, y):
    """Convert screen pixel coordinates (x, y) to matrix row and column indices [r, c]."""
    c = int((x + (SCREEN_SIZE / 2)) // GRID_SIZE)  # Calculate column index from horizontal pixel position
    r = int(((SCREEN_SIZE / 2) - y) // GRID_SIZE)  # Calculate row index from vertical pixel position
    return max(0, min(ROWS - 1, r)), max(0, min(COLS - 1, c))  # Clamp within matrix bounds [0, 99]

def grid_to_screen(r, c):
    """Convert matrix row and column indices [r, c] to centered screen pixel coordinates (x, y)."""
    x = (c * GRID_SIZE) - (SCREEN_SIZE / 2) + (GRID_SIZE / 2)  # Calculate x center pixel
    y = (SCREEN_SIZE / 2) - (r * GRID_SIZE) - (GRID_SIZE / 2)  # Calculate y center pixel
    return x, y                          # Return tuple of (x, y) screen coordinates

# 4. High-Speed Territory Rendering
def render_captured_area(captured_cells, player_id):
    """Render enclosed territory using Horizontal Scanline Run-Length compression (2-3 ms)."""
    rows = {}                            # Dictionary grouping column indices by row: {row: [c1, c2, ...]}
    for r, c in captured_cells:          # Iterate through all newly captured cells
        rows.setdefault(r, []).append(c) # Group columns into their respective row bucket

    t_stamper.color(COLOR_MAP[player_id]) # Set stamper color to the capturing player's territory color
    for r, cols in rows.items():         # Process each row with captured cells
        cols.sort()                      # Sort columns from left to right for contiguous grouping
        start_c = cols[0]                # Track start column of contiguous segment
        prev_c = start_c                 # Track previous column index
        for c in cols[1:]:               # Iterate through subsequent columns in the same row
            if c == prev_c + 1:          # Check if adjacent column continues the contiguous block
                prev_c = c               # Extend contiguous run
            else:
                # Stamp the contiguous strip
                length = prev_c - start_c + 1  # Calculate strip tile length
                center_c = (start_c + prev_c) / 2  # Calculate horizontal center column of the strip
                x, y = grid_to_screen(r, center_c)  # Get screen center position for stamping
                t_stamper.shapesize(stretch_wid=GRID_SIZE / 20, stretch_len=(length * GRID_SIZE) / 20)  # Scale shape
                t_stamper.goto(x, y)     # Move stamper to strip center
                t_stamper.stamp()        # Stamp contiguous horizontal block
                start_c = c              # Start a new contiguous segment
                prev_c = c               # Update previous column
        # Stamp final remaining contiguous segment in this row
        length = prev_c - start_c + 1    # Calculate final strip tile length
        center_c = (start_c + prev_c) / 2  # Calculate horizontal center column
        x, y = grid_to_screen(r, center_c)  # Get screen position
        t_stamper.shapesize(stretch_wid=GRID_SIZE / 20, stretch_len=(length * GRID_SIZE) / 20)  # Scale shape
        t_stamper.goto(x, y)             # Move stamper to strip center
        t_stamper.stamp()                # Stamp final block of the row

def drop_trail_stamp(r, c, trail_id, player_id):
    """Stamp a single trail tile on the board and record its stamp ID for instant removal."""
    grid[r][c] = trail_id                # Mark cell in grid matrix as player's trail
    x, y = grid_to_screen(r, c)          # Convert grid coordinates to screen pixel position
    tr_stamper.goto(x, y)                # Move trail stamper to cell position
    tr_stamper.color(COLOR_MAP[trail_id])  # Set trail color (Neon Pink or Neon Cyan)
    sid = tr_stamper.stamp()             # Stamp trail square and capture unique Turtle stamp ID
    trail_stamps[(r, c)] = sid           # Save stamp ID mapped to grid coordinates
    trail_stamps_owner[(r, c)] = player_id  # Save owner ID for fast selective removal

# 5. Inverted BFS Flood Fill Enclosure Conquest Algorithm
def close_loop_and_fill(player_id, trail_id):
    """Enclosure detection algorithm using Inverted BFS Flood Fill with a fast flat bytearray (<8 ms)."""
    boundary_1 = player_id               # First enclosure boundary: player's established territory
    boundary_2 = trail_id                # Second enclosure boundary: player's active trail

    visited = bytearray(TOTAL_CELLS)     # Allocate flat 10,000-byte array for C-speed lookup (0=Unvisited, 1=Outside)
    queue = deque()                      # Instantiate double-ended queue for BFS breadth-first search

    # Step 1: Seed left and right outer screen boundaries into queue
    for r in range(ROWS):                # Loop through all rows
        row_offset = r * COLS            # Compute 1D row index offset
        for c in (0, COLS - 1):          # Check leftmost (col 0) and rightmost (col 99) columns
            idx = row_offset + c         # Compute 1D cell index
            cell_val = grid[r][c]        # Fetch current grid cell value
            if cell_val != boundary_1 and cell_val != boundary_2:  # If cell is not a boundary
                visited[idx] = 1         # Mark cell as outside
                queue.append(idx)        # Push cell index to BFS queue

    # Step 2: Seed top and bottom outer screen boundaries into queue
    for c in range(COLS):                # Loop through all columns
        for r in (0, ROWS - 1):          # Check topmost (row 0) and bottommost (row 99) rows
            idx = r * COLS + c           # Compute 1D cell index
            cell_val = grid[r][c]        # Fetch current grid cell value
            if cell_val != boundary_1 and cell_val != boundary_2 and not visited[idx]:  # If unvisited non-boundary
                visited[idx] = 1         # Mark cell as outside
                queue.append(idx)        # Push cell index to BFS queue

    # Step 3: Traverse outside cells in 4 cardinal directions via BFS
    while queue:                         # Loop until all outside cells are explored
        curr = queue.popleft()           # Pop front cell index from queue
        r = curr // COLS                 # Extract row coordinate from 1D index
        c = curr % COLS                  # Extract column coordinate from 1D index

        # Inspect North Neighbor (Up)
        if r > 0:                        # Verify boundary constraint
            n = curr - COLS              # 1D index of north neighbor
            if not visited[n]:           # Check if neighbor has not yet been visited
                v = grid[r - 1][c]       # Get neighbor cell value
                if v != boundary_1 and v != boundary_2:  # Check if neighbor is not a wall
                    visited[n] = 1       # Mark neighbor as visited
                    queue.append(n)      # Add neighbor to queue

        # Inspect South Neighbor (Down)
        if r < ROWS - 1:                 # Verify boundary constraint
            n = curr + COLS              # 1D index of south neighbor
            if not visited[n]:           # Check if neighbor has not yet been visited
                v = grid[r + 1][c]       # Get neighbor cell value
                if v != boundary_1 and v != boundary_2:  # Check if neighbor is not a wall
                    visited[n] = 1       # Mark neighbor as visited
                    queue.append(n)      # Add neighbor to queue

        # Inspect West Neighbor (Left)
        if c > 0:                        # Verify boundary constraint
            n = curr - 1                 # 1D index of west neighbor
            if not visited[n]:           # Check if neighbor has not yet been visited
                v = grid[r][c - 1]       # Get neighbor cell value
                if v != boundary_1 and v != boundary_2:  # Check if neighbor is not a wall
                    visited[n] = 1       # Mark neighbor as visited
                    queue.append(n)      # Add neighbor to queue

        # Inspect East Neighbor (Right)
        if c < COLS - 1:                 # Verify boundary constraint
            n = curr + 1                 # 1D index of east neighbor
            if not visited[n]:           # Check if neighbor has not yet been visited
                v = grid[r][c + 1]       # Get neighbor cell value
                if v != boundary_1 and v != boundary_2:  # Check if neighbor is not a wall
                    visited[n] = 1       # Mark neighbor as visited
                    queue.append(n)      # Add neighbor to queue

    # Step 4: Identify all enclosed cells (unvisited = trapped inside boundaries)
    captured_cells = []                  # List to collect newly conquered cell coordinates
    for r in range(ROWS):                # Iterate through all rows
        row_offset = r * COLS            # Compute row offset
        for c in range(COLS):            # Iterate through all columns
            idx = row_offset + c         # Compute 1D cell index
            if not visited[idx] or grid[r][c] == trail_id:  # If cell is enclosed or part of active trail
                if grid[r][c] != player_id:  # Only update cells that are not already claimed
                    grid[r][c] = player_id   # Update cell ownership to capturing player
                    captured_cells.append((r, c))  # Append to captured list for rendering

    # Step 5: Clear old trail stamps from screen and replace with territory scanlines
    to_del = [pt for pt, pid in trail_stamps_owner.items() if pid == player_id]  # Collect player's trail points
    for pt in to_del:                    # Loop through points to remove
        try:
            tr_stamper.clearstamp(trail_stamps[pt])  # Delete individual trail stamp from screen
        except Exception:
            pass                         # Catch invalid stamp ID exceptions safely
        trail_stamps.pop(pt, None)       # Remove point from stamp ID registry
        trail_stamps_owner.pop(pt, None) # Remove point from owner registry

    if captured_cells:                   # Check if any cells were conquered
        render_captured_area(captured_cells, player_id)  # Render newly enclosed area in batch

    play_sfx("claim")                    # Play sound effect for successful territory capture

# 6. Collision Physics & Player Lifecycle
def clear_trail(trail_id):
    """Instantly remove all trail stamps of a player upon collision ('ชนหางหาย')."""
    owner_id = 1 if trail_id == 3 else 2 # Identify trail owner (3 -> Player 1, 4 -> Player 2)
    for r in range(ROWS):                # Iterate through all rows
        for c in range(COLS):            # Iterate through all columns
            if grid[r][c] == trail_id:   # Check if cell contains the target trail
                grid[r][c] = 0           # Reset cell state to empty space

    to_del = [pt for pt, pid in trail_stamps_owner.items() if pid == owner_id]  # Find owner's stamps
    for pt in to_del:                    # Loop through all trail coordinates
        try:
            tr_stamper.clearstamp(trail_stamps[pt])  # Erase visual stamp from screen
        except Exception:
            pass                         # Suppress exceptions
        trail_stamps.pop(pt, None)       # Remove coordinate from stamp dictionary
        trail_stamps_owner.pop(pt, None) # Remove coordinate from owner dictionary

def respawn_player(player_turtle, player_id):
    """Respawn player back at home base and reset movement state."""
    if player_id == 1:                   # Handling Player 1 respawn
        start_r, start_c = ROWS // 2, COLS // 5  # Home base matrix position (Row 50, Col 20)
        pos = grid_to_screen(start_r, start_c)   # Convert to screen pixel coordinates
        p1.goto(pos)                     # Move main core turtle to base
        p1_glow.goto(pos)                # Move glow aura turtle to base
        p1.direction = "stop"            # Halt movement
        p1.is_trail_active = False       # Reset trail activity flag
    else:                                # Handling Player 2 respawn
        start_r, start_c = ROWS // 2, (COLS * 4) // 5  # Home base matrix position (Row 50, Col 80)
        pos = grid_to_screen(start_r, start_c)         # Convert to screen pixel coordinates
        p2.goto(pos)                     # Move main core turtle to base
        p2_glow.goto(pos)                # Move glow aura turtle to base
        p2.direction = "stop"            # Halt movement
        p2.is_trail_active = False       # Reset trail activity flag

def trigger_game_over(winner_text, color=None):
    """Halt gameplay, hide player avatars, play victory/defeat sound, and display game over UI."""
    global game_state                    # Access global game_state variable
    game_state = "GAME_OVER"             # Switch active state to GAME_OVER
    stop_bgm()                           # Stop playing match background music
    p1.hideturtle()                      # Hide Player 1 core avatar
    p1_glow.hideturtle()                 # Hide Player 1 glow halo
    p2.hideturtle()                      # Hide Player 2 core avatar
    p2_glow.hideturtle()                 # Hide Player 2 glow halo
    draw_game_over(winner_text, color)   # Render Game Over screen with winner announcement

    p1_tiles = sum(row.count(1) for row in grid)  # Count total tiles conquered by Player 1
    p2_tiles = sum(row.count(2) for row in grid)  # Count total tiles conquered by Player 2
    if winner_text and "DRAW" in winner_text:     # Check if match ended in a draw
        play_sfx("game_over")            # Play game over sound effect
    elif winner_text is None and p1_tiles == p2_tiles:  # Check score tie on timeout
        play_sfx("game_over")            # Play game over sound effect
    else:
        play_sfx("win")                  # Play victory fanfare sound effect

def update_game_step():
    """Execute simultaneous movement update, collision checks, and trail generation each frame."""
    global game_state                    # Access global game_state variable

    if game_state != "PLAYING":          # Exit early if not in active playing state
        return

    p1_moving = (p1.direction != "stop") # Check if Player 1 is moving
    p2_moving = (p2.direction != "stop") # Check if Player 2 is moving

    if not p1_moving and not p2_moving:  # Exit early if both players are idle
        return

    curr_r1, curr_c1 = screen_to_grid(p1.xcor(), p1.ycor())  # Current grid coordinates of Player 1
    curr_r2, curr_c2 = screen_to_grid(p2.xcor(), p2.ycor())  # Current grid coordinates of Player 2

    # Calculate Next Step for Player 1
    next_r1, next_c1 = curr_r1, curr_c1  # Initialize candidate position
    if p1.direction == "up": next_r1 -= 1     # Move one tile up
    elif p1.direction == "down": next_r1 += 1 # Move one tile down
    elif p1.direction == "left": next_c1 -= 1 # Move one tile left
    elif p1.direction == "right": next_c1 += 1# Move one tile right

    # Calculate Next Step for Player 2
    next_r2, next_c2 = curr_r2, curr_c2  # Initialize candidate position
    if p2.direction == "up": next_r2 -= 1     # Move one tile up
    elif p2.direction == "down": next_r2 += 1 # Move one tile down
    elif p2.direction == "left": next_c2 -= 1 # Move one tile left
    elif p2.direction == "right": next_c2 += 1# Move one tile right

    # Boundary Collision Checks
    p1_valid = (0 <= next_r1 < ROWS and 0 <= next_c1 < COLS)  # Validate Player 1 stays inside arena
    p2_valid = (0 <= next_r2 < ROWS and 0 <= next_c2 < COLS)  # Validate Player 2 stays inside arena

    if not p1_valid:                     # Handle Player 1 hitting wall boundary
        next_r1, next_c1 = curr_r1, curr_c1  # Revert candidate position
        p1.direction = "stop"            # Stop Player 1 movement
    if not p2_valid:                     # Handle Player 2 hitting wall boundary
        next_r2, next_c2 = curr_r2, curr_c2  # Revert candidate position
        p2.direction = "stop"            # Stop Player 2 movement

    # Check 1: Head-on Collision -> Result: DRAW!
    same_cell = (next_r1 == next_r2 and next_c1 == next_c2) and (p1_moving or p2_moving)  # Stepping into same tile
    crossed_paths = (next_r1 == curr_r2 and next_c1 == curr_c2 and next_r2 == curr_r1 and next_c2 == curr_c1)  # Swapping tiles

    if same_cell or crossed_paths:       # Head-on collision occurred
        play_sfx("hit")                  # Play crash hit sound effect
        clear_trail(3)                   # Clear Player 1 trail immediately
        clear_trail(4)                   # Clear Player 2 trail immediately
        p1.is_trail_active = False       # Reset trail status
        p2.is_trail_active = False       # Reset trail status
        trigger_game_over("IT'S A DRAW! (HEAD-ON COLLISION)", "#ffe600")  # Declare draw match
        return

    # Check 2: Enemy Trail Cutting Collision
    target1 = grid[next_r1][next_c1] if (p1_moving and p1_valid) else None  # Tile Player 1 lands on
    target2 = grid[next_r2][next_c2] if (p2_moving and p2_valid) else None  # Tile Player 2 lands on

    p1_cuts_p2 = (target1 == 4)          # Player 1 cuts Player 2's trail (trail ID = 4)
    p2_cuts_p1 = (target2 == 3)          # Player 2 cuts Player 1's trail (trail ID = 3)

    # Mutual Simultaneous Tail Cut -> DRAW
    if p1_cuts_p2 and p2_cuts_p1:        # Both players sliced each other's trail at the exact same tick
        play_sfx("hit")                  # Play collision hit sound effect
        clear_trail(3)                   # Erase Player 1 trail
        clear_trail(4)                   # Erase Player 2 trail
        p1.is_trail_active = False       # Reset trail activity
        p2.is_trail_active = False       # Reset trail activity
        trigger_game_over("IT'S A DRAW! (MUTUAL TAIL CUT)", "#ffe600")  # Declare draw match
        return

    # Player 1 cuts Player 2's Trail
    if p1_cuts_p2:                       # Player 1 successfully cut Player 2's light trail
        play_sfx("hit")                  # Play collision sound effect
        clear_trail(4)                   # Erase Player 2 trail immediately ("ชนหางหาย")
        p2.is_trail_active = False       # Reset Player 2 trail activity
        if COLLISION_MODE == "ELIMINATION":
            trigger_game_over("PLAYER 1 (NEON PINK) WINS! (TAIL CUT)", "#ff007f")  # Declare Player 1 victory
            return
        else:
            respawn_player(p2, 2)        # Respawn Player 2 at home base

    # Player 2 cuts Player 1's Trail
    if p2_cuts_p1:                       # Player 2 successfully cut Player 1's light trail
        play_sfx("hit")                  # Play collision sound effect
        clear_trail(3)                   # Erase Player 1 trail immediately ("ชนหางหาย")
        p1.is_trail_active = False       # Reset Player 1 trail activity
        if COLLISION_MODE == "ELIMINATION":
            trigger_game_over("PLAYER 2 (NEON CYAN) WINS! (TAIL CUT)", "#00f0ff")  # Declare Player 2 victory
            return
        else:
            respawn_player(p1, 1)        # Respawn Player 1 at home base

    # Check 3: Movement Execution & Territory Enclosure
    if p1_moving and p1_valid:           # If Player 1 is actively moving
        pos1 = grid_to_screen(next_r1, next_c1)  # Calculate screen pixel destination
        p1.goto(pos1)                    # Move core avatar to new coordinates
        p1_glow.goto(pos1)               # Move glow aura to new coordinates
        t1 = grid[next_r1][next_c1]      # Fetch target cell value
        if t1 == 1:                      # Stepped back into own base
            if getattr(p1, "is_trail_active", False):  # If returning with an active trail
                close_loop_and_fill(1, 3)# Trigger enclosure flood fill algorithm
                p1.is_trail_active = False  # Deactivate trail flag
        elif t1 == 3:                    # Looped back onto own trail
            close_loop_and_fill(1, 3)    # Trigger enclosure flood fill algorithm
            p1.is_trail_active = False   # Deactivate trail flag
        else:
            drop_trail_stamp(next_r1, next_c1, 3, 1)  # Drop trail stamp on empty/enemy cell
            p1.is_trail_active = True    # Activate trail flag

    if p2_moving and p2_valid:           # If Player 2 is actively moving
        pos2 = grid_to_screen(next_r2, next_c2)  # Calculate screen pixel destination
        p2.goto(pos2)                    # Move core avatar to new coordinates
        p2_glow.goto(pos2)               # Move glow aura to new coordinates
        t2 = grid[next_r2][next_c2]      # Fetch target cell value
        if t2 == 2:                      # Stepped back into own base
            if getattr(p2, "is_trail_active", False):  # If returning with an active trail
                close_loop_and_fill(2, 4)# Trigger enclosure flood fill algorithm
                p2.is_trail_active = False  # Deactivate trail flag
        elif t2 == 4:                    # Looped back onto own trail
            close_loop_and_fill(2, 4)    # Trigger enclosure flood fill algorithm
            p2.is_trail_active = False   # Deactivate trail flag
        else:
            drop_trail_stamp(next_r2, next_c2, 4, 2)  # Drop trail stamp on empty/enemy cell
            p2.is_trail_active = True    # Activate trail flag

def reset_game():
    """Reset board matrix, stamps, player coordinates, and spawn 5x5 starting bases."""
    global grid                          # Access global grid variable

    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]  # Re-initialize empty 100x100 grid matrix
    t_stamper.clearstamps()              # Clear all territory stamps from screen
    tr_stamper.clearstamps()             # Clear all trail stamps from screen
    trail_stamps.clear()                 # Clear trail stamp registry
    trail_stamps_owner.clear()           # Clear trail owner registry

    # Reset Player 1 Position (Left Side)
    p1_start_r, p1_start_c = ROWS // 2, COLS // 5  # Spawn coordinates (Row 50, Col 20)
    pos1 = grid_to_screen(p1_start_r, p1_start_c)   # Screen pixel coordinates
    p1.goto(pos1)                        # Move core avatar to starting position
    p1_glow.goto(pos1)                   # Move glow aura to starting position
    p1.direction = "stop"                # Set initial direction to stopped
    p1.is_trail_active = False           # Clear trail flag
    p1_glow.showturtle()                 # Show glow avatar
    p1.showturtle()                      # Show core avatar

    # Reset Player 2 Position (Right Side)
    p2_start_r, p2_start_c = ROWS // 2, (COLS * 4) // 5  # Spawn coordinates (Row 50, Col 80)
    pos2 = grid_to_screen(p2_start_r, p2_start_c)         # Screen pixel coordinates
    p2.goto(pos2)                        # Move core avatar to starting position
    p2_glow.goto(pos2)                   # Move glow aura to starting position
    p2.direction = "stop"                # Set initial direction to stopped
    p2.is_trail_active = False           # Clear trail flag
    p2_glow.showturtle()                 # Show glow avatar
    p2.showturtle()                      # Show core avatar

    # Create 5x5 Initial Base Territories
    p1_base = []                         # Collect Player 1 starting base coordinates
    p2_base = []                         # Collect Player 2 starting base coordinates
    for dr in range(-BASE_RADIUS, BASE_RADIUS + 1):  # Loop through vertical radius (-2 to +2)
        for dc in range(-BASE_RADIUS, BASE_RADIUS + 1):  # Loop through horizontal radius (-2 to +2)
            r1, c1 = p1_start_r + dr, p1_start_c + dc  # Player 1 base cell
            r2, c2 = p2_start_r + dr, p2_start_c + dc  # Player 2 base cell
            grid[r1][c1] = 1             # Mark cell as Player 1 base
            p1_base.append((r1, c1))     # Add to Player 1 base list
            grid[r2][c2] = 2             # Mark cell as Player 2 base
            p2_base.append((r2, c2))     # Add to Player 2 base list

    render_captured_area(p1_base, 1)     # Render Player 1 starting base on screen
    render_captured_area(p2_base, 2)     # Render Player 2 starting base on screen

# =============================================================================
# Input Handling
# =============================================================================

# --- Player 1 Direction Handlers (WASD) ---
def p1_up():
    """Steer Player 1 upward (prevents 180-degree instant reversal)."""
    if game_state == "PLAYING" and p1.direction != "down":  # Ignore if moving down or not playing
        p1.direction = "up"              # Set direction to up

def p1_down():
    """Steer Player 1 downward (prevents 180-degree instant reversal)."""
    if game_state == "PLAYING" and p1.direction != "up":    # Ignore if moving up or not playing
        p1.direction = "down"            # Set direction to down

def p1_left():
    """Steer Player 1 leftward (prevents 180-degree instant reversal)."""
    if game_state == "PLAYING" and p1.direction != "right": # Ignore if moving right or not playing
        p1.direction = "left"            # Set direction to left

def p1_right():
    """Steer Player 1 rightward (prevents 180-degree instant reversal)."""
    if game_state == "PLAYING" and p1.direction != "left":  # Ignore if moving left or not playing
        p1.direction = "right"           # Set direction to right

# --- Player 2 Direction Handlers (Arrow Keys) ---
def p2_up():
    """Steer Player 2 upward (prevents 180-degree instant reversal)."""
    if game_state == "PLAYING" and p2.direction != "down":  # Ignore if moving down or not playing
        p2.direction = "up"              # Set direction to up

def p2_down():
    """Steer Player 2 downward (prevents 180-degree instant reversal)."""
    if game_state == "PLAYING" and p2.direction != "up":    # Ignore if moving up or not playing
        p2.direction = "down"            # Set direction to down

def p2_left():
    """Steer Player 2 leftward (prevents 180-degree instant reversal)."""
    if game_state == "PLAYING" and p2.direction != "right": # Ignore if moving right or not playing
        p2.direction = "left"            # Set direction to left

def p2_right():
    """Steer Player 2 rightward (prevents 180-degree instant reversal)."""
    if game_state == "PLAYING" and p2.direction != "left":  # Ignore if moving left or not playing
        p2.direction = "right"           # Set direction to right

# Bind Keyboard Inputs to Handlers
wn.listen()                              # Enable window to listen for keyboard events
wn.onkeypress(p1_up, "w")                # Bind 'w' key to Player 1 Up
wn.onkeypress(p1_down, "s")              # Bind 's' key to Player 1 Down
wn.onkeypress(p1_left, "a")              # Bind 'a' key to Player 1 Left
wn.onkeypress(p1_right, "d")             # Bind 'd' key to Player 1 Right
wn.onkeypress(p1_up, "W")                # Bind uppercase 'W' key
wn.onkeypress(p1_down, "S")              # Bind uppercase 'S' key
wn.onkeypress(p1_left, "A")              # Bind uppercase 'A' key
wn.onkeypress(p1_right, "D")             # Bind uppercase 'D' key

wn.onkeypress(p2_up, "Up")               # Bind Up Arrow to Player 2 Up
wn.onkeypress(p2_down, "Down")           # Bind Down Arrow to Player 2 Down
wn.onkeypress(p2_left, "Left")           # Bind Left Arrow to Player 2 Left
wn.onkeypress(p2_right, "Right")         # Bind Right Arrow to Player 2 Right

# --- Mouse Click Handler ---
def handle_click(x, y):
    """Process mouse click events for menu duration buttons, Start, and Play Again buttons."""
    global game_state, selected_time, start_time_stamp  # Global variables modified on click

    if game_state == "MENU":             # Handle clicks on Main Menu screen
        # Check 10s Match Duration Button (-160 <= x <= -80, -70 <= y <= -30)
        if -160 <= x <= -80 and -70 <= y <= -30:
            selected_time = 10           # Select 10 seconds duration
            play_sfx("click")            # Play button click sound
            draw_menu()                  # Redraw menu to update selected button visual

        # Check 30s Match Duration Button (-40 <= x <= 40, -70 <= y <= -30)
        elif -40 <= x <= 40 and -70 <= y <= -30:
            selected_time = 30           # Select 30 seconds duration
            play_sfx("click")            # Play button click sound
            draw_menu()                  # Redraw menu to update selected button visual

        # Check 60s Match Duration Button (80 <= x <= 160, -70 <= y <= -30)
        elif 80 <= x <= 160 and -70 <= y <= -30:
            selected_time = 60           # Select 60 seconds duration
            play_sfx("click")            # Play button click sound
            draw_menu()                  # Redraw menu to update selected button visual

        # Check 'START GAME' Button (-90 <= x <= 90, -155 <= y <= -105)
        elif -90 <= x <= 90 and -155 <= y <= -105:
            play_sfx("click")            # Play button click sound
            pen.clear()                  # Clear menu graphics
            reset_game()                 # Reset board and player positions
            start_time_stamp = time.time()  # Record start timestamp
            game_state = "PLAYING"       # Transition state to PLAYING
            play_bgm("playing")          # Switch to battle background music

    elif game_state == "GAME_OVER":      # Handle clicks on Game Over screen
        # Check 'PLAY AGAIN' Button (-90 <= x <= 90, -85 <= y <= -35)
        if -90 <= x <= 90 and -85 <= y <= -35:
            play_sfx("click")            # Play button click sound
            clear_trail(3)               # Clear Player 1 trail
            clear_trail(4)               # Clear Player 2 trail
            t_stamper.clearstamps()      # Erase territory stamps
            tr_stamper.clearstamps()     # Erase trail stamps
            game_state = "MENU"          # Transition state back to MENU
            draw_menu()                  # Render main menu
            play_bgm("lobby")            # Switch back to lobby background music

# Bind Mouse Click Event
wn.onscreenclick(handle_click)           # Attach click handler function to screen click event

# =============================================================================
# Main Game Loop
# =============================================================================

def draw_button(x, y, w, h, text, bg_color, text_color="white"):
    """Draw a centered rectangular button with filled background and text label."""
    pen.goto(x - w / 2, y - h / 2)       # Move pen to bottom-left corner of button
    pen.color(bg_color)                  # Set button fill and stroke color
    pen.begin_fill()                     # Begin shape fill

    for _ in range(2):                   # Loop twice to draw two pairs of equal sides
        pen.forward(w)                   # Draw horizontal button edge
        pen.left(90)                     # Turn left 90 degrees
        pen.forward(h)                   # Draw vertical button edge
        pen.left(90)                     # Turn left 90 degrees

    pen.end_fill()                       # Complete shape fill
    pen.goto(x, y - 10)                  # Position pen for centered label text
    pen.color(text_color)                # Set text label color
    pen.write(text, align="center", font=("Courier", 14, "bold"))  # Render button label text

def draw_menu():
    """Render Main Menu: Title banner, control schemes, duration selectors, and Start button."""
    pen.clear()                          # Clear existing screen drawings

    # Draw Game Title Banner
    pen.goto(0, 160)                     # Position pen for title text
    pen.color("#ffe600")                 # Set title color to neon yellow gold
    pen.write("DON'T TOUCH MY AREA", align="center", font=("Courier", 26, "bold"))  # Render title

    # Draw Player 1 Controls Box
    pen.goto(-150, 80)                   # Position pen for Player 1 instructions
    pen.color("#ff007f")                 # Set text color to Neon Pink
    pen.write("PLAYER 1 (Neon Pink)\nWASD Keys", align="center", font=("Courier", 13, "bold"))  # Render P1 instructions

    # Draw Player 2 Controls Box
    pen.goto(150, 80)                    # Position pen for Player 2 instructions
    pen.color("#00f0ff")                 # Set text color to Neon Cyan
    pen.write("PLAYER 2 (Neon Cyan)\nArrow Keys", align="center", font=("Courier", 13, "bold"))  # Render P2 instructions

    # Draw Match Duration Section Header
    pen.goto(0, -10)                     # Position pen for duration prompt
    pen.color("white")                   # Set text color to white
    pen.write("SELECT MATCH DURATION", align="center", font=("Courier", 14, "bold"))  # Render duration prompt

    # Draw Duration Selection Buttons (10s, 30s, 60s)
    times = [10, 30, 60]                 # Match duration options in seconds
    x_pos = [-120, 0, 120]               # Horizontal positions for duration buttons

    for t, x in zip(times, x_pos):       # Loop over each duration option and position
        is_selected = (t == selected_time)  # Check if this duration is currently selected
        bg_color = "#ffe600" if is_selected else "#1f2937"  # Electric Yellow for active timer, dark gray for inactive
        txt_color = "#1a1a1a" if is_selected else "white"   # Dark text for high contrast on active yellow button
        draw_button(x, -50, 80, 40, f"{t}s", bg_color, txt_color)  # Draw duration button

    # Draw 'START GAME' Button
    draw_button(0, -130, 180, 50, "START GAME", "#00ff88")  # Draw bright green Start button

def draw_game_over(winner_text=None, color=None):
    """Render Game Over Screen: Winner banner, total score & territory percentage, and Play Again button."""
    pen.clear()                          # Clear active screen text

    # Top Title Banner
    pen.goto(0, 150)                     # Move pen to top header position
    pen.color("#ffe600")                 # Set banner color to neon gold
    pen.write("DON'T TOUCH MY AREA", align="center", font=("Courier", 24, "bold"))  # Render header

    p1_tiles = sum(row.count(1) for row in grid)  # Calculate total captured tiles for Player 1
    p2_tiles = sum(row.count(2) for row in grid)  # Calculate total captured tiles for Player 2

    # Determine Winner Text and Color if not provided directly
    if winner_text is None:              # Automatic timeout resolution
        if p1_tiles > p2_tiles:
            winner_text = "PLAYER 1 (NEON PINK) WINS!"  # Player 1 won by score
            color = "#ff007f"            # Neon Pink
        elif p2_tiles > p1_tiles:
            winner_text = "PLAYER 2 (NEON CYAN) WINS!"  # Player 2 won by score
            color = "#00f0ff"            # Neon Cyan
        else:
            winner_text = "IT'S A DRAW!" # Match ended in tie
            color = "#ffe600"            # Neon Gold
    elif color is None:                  # Infer color from winner text
        if "DRAW" in winner_text:
            color = "#ffe600"
        elif "1" in winner_text or "RED" in winner_text or "PINK" in winner_text:
            color = "#ff007f"
        else:
            color = "#00f0ff"

    # Draw Winner Announcement
    pen.goto(0, 80)                      # Move pen to announcement position
    pen.color(color)                     # Set winner accent color
    pen.write(winner_text, align="center", font=("Courier", 20, "bold"))  # Render announcement

    # Calculate Territory Conquest Percentages
    p1_pct = (p1_tiles / TOTAL_CELLS) * 100  # Player 1 captured percentage
    p2_pct = (p2_tiles / TOTAL_CELLS) * 100  # Player 2 captured percentage

    # Draw Final Scores and Percentages
    pen.goto(0, 20)                      # Position pen for score summary
    pen.color("white")                   # Set score color to white
    pen.write(
        f"P1: {p1_tiles} ({p1_pct:.1f}%) | P2: {p2_tiles} ({p2_pct:.1f}%)",
        align="center",
        font=("Courier", 15, "bold")
    )                                    # Render score and percentage summary

    # Draw 'PLAY AGAIN' Button
    draw_button(0, -60, 180, 50, "PLAY AGAIN", "#00ff88")  # Draw green Play Again button

def update_hud():
    """Update top HUD bar: Calculate countdown timer, show live scores, and handle timeout."""
    global game_state, time_left         # Access global variables

    if game_state != "PLAYING":          # Only update HUD during active play
        return

    elapsed = time.time() - start_time_stamp  # Calculate elapsed match time in seconds
    time_left = max(0, int(selected_time - elapsed))  # Calculate remaining time

    p1_tiles = sum(row.count(1) for row in grid)  # Live count of Player 1 territory tiles
    p2_tiles = sum(row.count(2) for row in grid)  # Live count of Player 2 territory tiles

    pen.clear()                          # Clear previous HUD text
    pen.goto(0, (SCREEN_SIZE / 2) + 12)  # Position pen above upper arena border
    timer_color = "#ffe600" if time_left <= 5 else "white"  # Turn neon yellow during final 5 seconds
    pen.color(timer_color)               # Set HUD text color
    pen.write(
        f"P1: {p1_tiles} pts | TIME: {time_left}s | P2: {p2_tiles} pts",
        align="center",
        font=("Courier", 13, "bold")
    )                                    # Render updated HUD statistics

    # Beep Warning Sound during final 5 seconds
    if 0 < time_left <= 5 and getattr(update_hud, "last_beep", None) != time_left:
        update_hud.last_beep = time_left # Cache beep timestamp
        play_sfx("click")                # Play warning beep sound

    # Timeout Trigger
    if time_left <= 0:                   # Check if countdown reached zero
        trigger_game_over(None, None)    # Trigger game over by score calculation

# Initial Menu Render & BGM Playback
draw_menu()                              # Draw Main Menu on initial startup
play_bgm("lobby")                        # Start playing lobby background music

def game_loop():
    """Master game loop: Update physics tick, refresh HUD, render frame, and schedule next tick."""
    if game_state == "PLAYING":          # Run physics and HUD only while playing
        update_game_step()               # Execute movement and collision physics
        update_hud()                     # Refresh countdown and territory score

    try:
        wn.update()                      # Render all buffered draw calls to screen in one frame
        wn.ontimer(game_loop, 25)        # Schedule next game loop tick in 25 ms (~40 FPS) and significantly for player Speed 
    except (turtle.Terminator, Exception):
        stop_bgm()                       # Stop background music playback cleanly on exit

# Launch Game Loop & Event Listener
game_loop()                              # Start game loop cycle
wn.mainloop()                            # Hand execution over to Turtle main event loop