import pyautogui
import time


def press_f5_every_x_seconds(interval_seconds: int):
    try:
        while True:
            # 模拟按下 F5 键
            pyautogui.press('f5')
            print(f"Pressed F5, waiting for {interval_seconds} seconds.")
            # 等待指定的时间间隔
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Program exited by user.")


# 调用函数，设定每隔 10 秒按一次 F5
press_f5_every_x_seconds(30)
