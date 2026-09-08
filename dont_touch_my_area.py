import turtle
import time
from collections import deque

SCREEN_SIZE = 600
GRID_SIZE = 40
COLS = SCREEN_SIZE // GRID_SIZE  # 30 ช่อง
ROWS = SCREEN_SIZE // GRID_SIZE  # 30 ช่อง

# ค่าสถานะใน 2D Array:
# 0 = ช่องว่าง (Empty)
# 1 = แดนถาวร P1,  2 = แดนถาวร P2
# 3 = หางชั่วคราว P1, 4 = หางชั่วคราว P2
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# ===========================================
# SCREEN & RENDERER SETUP
# ===========================================
wn = turtle.Screen()
wn.title("2D Array Territory Fill")
wn.bgcolor("#1a1a1a")
wn.setup(width=SCREEN_SIZE, height=SCREEN_SIZE)
wn.tracer(0)

# เต่าสำหรับวาดช่องสี่เหลี่ยมตามค่าใน Grid
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
    """แปลงพิกัดหน้าจอ (Pixel) เป็น Index ของ Matrix [row][col]"""
    c = int((x + (SCREEN_SIZE / 2)) // GRID_SIZE)
    r = int(((SCREEN_SIZE / 2) - y) // GRID_SIZE)
    return max(0, min(ROWS - 1, r)), max(0, min(COLS - 1, c))

def grid_to_screen(r, c):
    """แปลง Index ของ Matrix เป็นพิกัดกึ่งกลางช่องบนหน้าจอ"""
    x = (c * GRID_SIZE) - (SCREEN_SIZE / 2) + (GRID_SIZE / 2)
    y = (SCREEN_SIZE / 2) - (r * GRID_SIZE) - (GRID_SIZE / 2)
    return x, y

# ===========================================
# MATRIX FLOOD FILL LOGIC
# ===========================================
def close_loop_and_fill(player_id, trail_id):
    """
    เมื่อหัวชนหาง:
    1. นำน้ำท่วมจากขอบนอกของ Matrix (ช่องว่างที่ไม่ถูกล้อม)
    2. ช่องด้านในที่น้ำเข้าไม่ถึง + เส้น trail ทั้งหมด จะกลายเป็น player_id ถาวร
    """
    # ผนังปิดล้อม = ช่องที่เป็นแดนตัวเอง หรือเส้นหางของตัวเอง
    boundary_values = {player_id, trail_id}
    
    visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
    queue = deque()

    # ใส่ขอบทั้ง 4 ด้านของ Matrix เข้าคิวเริ่มต้น
    for r in range(ROWS):
        for c in [0, COLS - 1]:
            if grid[r][c] not in boundary_values:
                visited[r][c] = True
                queue.append((r, c))
                
    for c in range(COLS):
        for r in [0, ROWS - 1]:
            if grid[r][c] not in boundary_values and not visited[r][c]:
                visited[r][c] = True
                queue.append((r, c))

    # จำลองน้ำท่วมเฉพาะบริเวณด้านนอก
    while queue:
        cr, cc = queue.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = cr + dr, cc + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if not visited[nr][nc] and grid[nr][nc] not in boundary_values:
                    visited[nr][nc] = True
                    queue.append((nr, nc))

    # อัปเดต Matrix: ช่องที่ไม่ถูกน้ำท่วม (visited == False) หรือเป็น trail ให้เป็นแดนถาวรทั้งหมด
    for r in range(ROWS):
        for c in range(COLS):
            if not visited[r][c] or grid[r][c] == trail_id:
                grid[r][c] = player_id

def render_grid():
    """เรนเดอร์สีจาก 2D Matrix"""
    drawer.clear()
    COLOR_MAP = {
        1: "#e74c3c",  # P1 แดนถาวร (แดงเข้ม)
        3: "#ff7675",  # P1 หางชั่วคราว (แดงอ่อน)
        2: "#0984e3",  # P2 แดนถาวร (น้ำเงินเข้ม)
        4: "#74b9ff"   # P2 หางชั่วคราว (ฟ้าอ่อน)
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

# วางตำแหน่งเริ่มต้น P1
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
        
        # คำนวณพิกัดก้าวถัดไป
        next_r, next_c = curr_r, curr_c
        if p1.direction == "up": next_r -= 1
        elif p1.direction == "down": next_r += 1
        elif p1.direction == "left": next_c -= 1
        elif p1.direction == "right": next_c += 1

        # ขอบจอ
        if 0 <= next_r < ROWS and 0 <= next_c < COLS:
            target_cell = grid[next_r][next_c]
            
            # ย้ายหัว
            p1.goto(grid_to_screen(next_r, next_c))

            # ตรวจสอบว่าหัวชนหางตัวเอง (3) หรือชนแดนเดิม (1) ขณะที่มีหางอยู่
            if target_cell in (1, 3):
                # เติมเต็มและรวมหางเป็นพื้นที่เดียวกัน
                close_loop_and_fill(player_id=1, trail_id=3)
            else:
                # ยังไม่ชน: ปั๊มค่าช่องใหม่เป็นหางชั่วคราว
                grid[next_r][next_c] = 3

    render_grid()
    wn.update()
    time.sleep(0.1)