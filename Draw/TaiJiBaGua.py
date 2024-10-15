import turtle

screen = turtle.Screen()
screen.bgcolor("white")
pen = turtle.Turtle()
pen.speed(0)


def draw_circle(radius, color):
    pen.penup()
    pen.goto(0, -radius)  # 将笔移动到圆的起始位置
    pen.pendown()
    pen.color(color)
    pen.begin_fill()
    pen.circle(radius)
    pen.end_fill()


def draw_star(size, color):
    pen.penup()
    pen.goto(-90, 30)  # 将笔移动到五角星的起始位置
    pen.setheading(0)      # 设置朝向
    pen.pendown()
    pen.color(color)
    pen.begin_fill()
    for _ in range(5):
        pen.forward(180)
        pen.right(144)
    pen.end_fill()


pen.hideturtle()
draw_circle(400, 'crimson')
draw_circle(300, 'white')
draw_circle(200, 'crimson')
draw_circle(100, 'blue')
draw_star(180, 'white')
turtle.done()
