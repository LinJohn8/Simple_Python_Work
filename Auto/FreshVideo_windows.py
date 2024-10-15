from pynput.mouse import Controller, Button
import screeninfo
import time

# 导入鼠标控制
mouse = Controller()

# 获取所有屏幕信息
screens = screeninfo.get_monitors()

# 确认使用第二个屏幕（索引从0开始，所以第二个屏幕是screens[1]）
second_screen = screens[1]


# 无限滚动
try:
    while True:

        mouse.position = (second_screen.x + second_screen.width // 4,
                          second_screen.y + second_screen.height // 4)
        time.sleep(1)
        mouse.click(Button.left)
        time.sleep(1)
        mouse.scroll(0, -3)  # 第一个参数是水平滚动，第二个是垂直滚动        # 垂直方向滚动（负数表示向下滚动）
        time.sleep(1)  # 每次滚动后暂停

        mouse.position = (second_screen.x + second_screen.width // 1.5,
                          second_screen.y + second_screen.height // 1.5)
        time.sleep(1)
        mouse.click(Button.left)
        time.sleep(1)
        mouse.scroll(0, -3)  # 第一个参数是水平滚动，第二个是垂直滚动        # 垂直方向滚动（负数表示向下滚动）
        time.sleep(1)  # 每次滚动后暂停

        mouse.position = (second_screen.x + second_screen.width // 1.5,
                          second_screen.y + second_screen.height // 4)
        time.sleep(1)
        mouse.click(Button.left)
        time.sleep(1)
        mouse.scroll(0, -3)  # 第一个参数是水平滚动，第二个是垂直滚动        # 垂直方向滚动（负数表示向下滚动）
        time.sleep(1)  # 每次滚动后暂停

        mouse.position = (second_screen.x + second_screen.width // 4,
                          second_screen.y + second_screen.height // 1.5)
        time.sleep(1)
        mouse.click(Button.left)
        time.sleep(1)
        mouse.scroll(0, -3)  # 第一个参数是水平滚动，第二个是垂直滚动        # 垂直方向滚动（负数表示向下滚动）
        time.sleep(1)  # 每次滚动后暂停
except KeyboardInterrupt:
    print("滚动停止")
