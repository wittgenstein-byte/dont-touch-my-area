import turtle
import time
import random

delay = 0.1
score1 = 0
score2 = 0

# Screen setup
wn = turtle.Screen()
wn.title("Snake Game - 2 Players")
wn.bgcolor("black")
wn.setup(width=1000, height=1000)
wn.tracer(0)

# ===========================================
# SNAKE 1 (Green - WASD)
# ===========================================
head1 = turtle.Turtle()
head1.speed(0)
head1.shape("square")
head1.color("green")
head1.penup()
head1.goto(-100, 0)
head1.direction = "stop"
segments1 = []

# ===========================================
# SNAKE 2 (Orange - Arrow Keys)
# ===========================================
head2 = turtle.Turtle()
head2.speed(0)
head2.shape("square")
head2.color("orange")
head2.penup()
head2.goto(100, 0)
head2.direction = "stop"
segments2 = []

# ===========================================
# FOOD
# ===========================================
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("red")
food.penup()
food.goto(0, 100)

# ===========================================
# SCOREBOARD
# ===========================================
pen = turtle.Turtle()
pen.speed(0)
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)

def update_scoreboard():
    pen.clear()
    pen.write(f"Player 1 (Green): {score1}    Player 2 (Orange): {score2}", 
              align="center", font=("Courier", 16, "bold"))

update_scoreboard()

# ===========================================
# MOVEMENT FUNCTIONS
# ===========================================
# Controls for Player 1
def p1_up():
    if head1.direction != "down":
        head1.direction = "up"

def p1_down():
    if head1.direction != "up":
        head1.direction = "down"

def p1_left():
    if head1.direction != "right":
        head1.direction = "left"

def p1_right():
    if head1.direction != "left":
        head1.direction = "right"

# Controls for Player 2
def p2_up():
    if head2.direction != "down":
        head2.direction = "up"

def p2_down():
    if head2.direction != "up":
        head2.direction = "down"

def p2_left():
    if head2.direction != "right":
        head2.direction = "left"

def p2_right():
    if head2.direction != "left":
        head2.direction = "right"

def move_snake(head):
    if head.direction == "up":
        head.sety(head.ycor() + 20)
    elif head.direction == "down":
        head.sety(head.ycor() - 20)
    elif head.direction == "left":
        head.setx(head.xcor() - 20)
    elif head.direction == "right":
        head.setx(head.xcor() + 20)

def reset_game():
    global score1, score2, delay
    time.sleep(1)
    
    # รีเซ็ตตำแหน่งหัว
    head1.goto(-100, 0)
    head1.direction = "stop"
    head2.goto(100, 0)
    head2.direction = "stop"

    # ซ่อนลำตัวเก่า
    for s in segments1:
        s.goto(1000, 1000)
    segments1.clear()

    for s in segments2:
        s.goto(1000, 1000)
    segments2.clear()

    score1 = 0
    score2 = 0
    delay = 0.1
    update_scoreboard()

# ===========================================
# KEYBOARD BINDINGS
# ===========================================
wn.listen()

# Player 1: WASD
wn.onkeypress(p1_up, "w")
wn.onkeypress(p1_up, "W")
wn.onkeypress(p1_down, "s")
wn.onkeypress(p1_down, "S")
wn.onkeypress(p1_left, "a")
wn.onkeypress(p1_left, "A")
wn.onkeypress(p1_right, "d")
wn.onkeypress(p1_right, "D")

# Player 2: Arrow Keys
wn.onkeypress(p2_up, "Up")
wn.onkeypress(p2_down, "Down")
wn.onkeypress(p2_left, "Left")
wn.onkeypress(p2_right, "Right")

# ===========================================
# MAIN GAME LOOP
# ===========================================
while True:
    wn.update()

    # 1. เช็กการชนขอบจอ (กว้าง 800 สูง 600 -> ขอบคือ x: ±390, y: ±290)
    if (abs(head1.xcor()) > 390 or abs(head1.ycor()) > 290 or
        abs(head2.xcor()) > 390 or abs(head2.ycor()) > 290):
        reset_game()

    # 2. กินอาหาร: Player 1
    if head1.distance(food) < 20:
        food.goto(random.randint(-370, 370), random.randint(-270, 240))
        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("#32CD32")  # เขียวอ่อน
        new_segment.penup()
        segments1.append(new_segment)
        score1 += 10
        delay = max(0.04, delay - 0.002)
        update_scoreboard()

    # 3. กินอาหาร: Player 2
    if head2.distance(food) < 20:
        food.goto(random.randint(-370, 370), random.randint(-270, 240))
        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("#FFA500")  # ส้มอ่อน
        new_segment.penup()
        segments2.append(new_segment)
        score2 += 10
        delay = max(0.04, delay - 0.002)
        update_scoreboard()

    # 4. ขยับลำตัวตามหัว (ไล่จากข้อสุดท้ายมาหาข้อแรก)
    for i in range(len(segments1) - 1, 0, -1):
        x = segments1[i - 1].xcor()
        y = segments1[i - 1].ycor()
        segments1[i].goto(x, y)
    if len(segments1) > 0:
        segments1[0].goto(head1.xcor(), head1.ycor())

    for i in range(len(segments2) - 1, 0, -1):
        x = segments2[i - 1].xcor()
        y = segments2[i - 1].ycor()
        segments2[i].goto(x, y)
    if len(segments2) > 0:
        segments2[0].goto(head2.xcor(), head2.ycor())

    # 5. ขยับหัวงู
    move_snake(head1)
    move_snake(head2)

    # 6. ตรวจการชนตัวเอง
    for s in segments1:
        if s.distance(head1) < 20:
            reset_game()
            break

    for s in segments2:
        if s.distance(head2) < 20:
            reset_game()
            break

    # 7. ตรวจการชนกันเองระหว่าง 2 ผู้เล่น (หัวชนหัว หรือ หัวชนลำตัวอีกฝ่าย)
    if head1.distance(head2) < 20:
        reset_game()

    for s in segments2:
        if head1.distance(s) < 20:
            reset_game()
            break

    for s in segments1:
        if head2.distance(s) < 20:
            reset_game()
            break

    time.sleep(delay)