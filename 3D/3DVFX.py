import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from random import randint, uniform
import math
from OpenGL.GLU import gluPerspective

# 初始化Pygame
pygame.init()

# 窗口大小
width, height = 800, 600

# 初始化Pygame显示
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)

# 透视投影设置
gluPerspective(45, (width / height), 0.1, 50.0)

# 初始摄像机位置
glTranslatef(0.0, 0.0, -5)


# 粒子类
class Particle:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.size = uniform(0.01, 0.05)
        self.speed_x = uniform(-0.1, 0.1)
        self.speed_y = uniform(-0.1, 0.1)
        self.speed_z = uniform(0.1, 0.5)
        self.color = (uniform(0, 1), uniform(0, 1), uniform(0, 1))

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.z += self.speed_z

    def draw(self):
        glBegin(GL_POINTS)
        glColor3f(*self.color)
        glVertex3f(self.x, self.y, self.z)
        glEnd()


# 创建粒子列表
particles = [Particle() for _ in range(10000)]

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    glRotatef(1, 3, 1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # 绘制粒子
    for particle in particles:
        particle.update()
        particle.draw()

    pygame.display.flip()
    pygame.time.wait(30)

# 退出程序
pygame.quit()