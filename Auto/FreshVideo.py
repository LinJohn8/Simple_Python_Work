"""
控制手机上刷屏幕，循环时间为2小时，每次上刷屏幕后随机等待1——20秒，当循环结束，关闭手机屏幕
"""
import random
import subprocess
import time

# 获取当前时间的时间戳
start_time = time.time()

# 设置循环的持续时间为2小时（以秒为单位）
duration = 2 * 60 * 60

# 假设手机已经连接并启用了ADB调试模式（下面会说明）
# 确保你已经安装了ADB工具，并将其路径添加到系统环境变量中

def swipe_up():
    while True:
        # 在这里写入你想要重复执行的代码

        subprocess.run(["adb", "shell", "input", "swipe", "500", "1500", "500", "1000", "200"])
        # 检查是否已经达到循环的持续时间
        elapsed_time = time.time() - start_time
        if elapsed_time >= duration:
            break
        # 生成随机的休眠时间在 1 到 20 秒之间
        sleep_time = random.randint(1, 5)
        should_swipe = random.choice([True, False])
        if should_swipe:
            for _ in range(5):
                # 执行点击命令
                subprocess.run(["adb", "shell", "input", "tap", str(500), str(1000)])
                time.sleep(0.1)
        # 休眠一段时间，以避免循环过于频繁
        time.sleep(sleep_time)

    print("循环结束")


def turn_off_screen():
    subprocess.run(["adb", "shell", "input", "keyevent", "26"])


# 假设手机已经连接并启用了ADB调试模式
# 确保你已经安装了ADB工具，并将其路径添加到系统环境变量中
swipe_up()
turn_off_screen()

