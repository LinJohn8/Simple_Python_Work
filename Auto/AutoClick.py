import pyautogui
import time

# 指定你要搜索的图片路径
image_path = "click.jpg"  # 替换成你的图片路径

# 检查屏幕上是否有图片，并点击
def check_and_click_image(image_path):
    # 查找屏幕上的图像并返回位置
    location = pyautogui.locateOnScreen(image_path, confidence=1)  # 使用较低的confidence提高速度
    print(1)
    if location:
        # 获取图像的中心位置并点击
        center = pyautogui.center(location)
        pyautogui.click(center)
        print(f"已点击图标，位置: {center}")
    else:
        # 如果找不到图像，可以选择不输出任何信息，避免不必要的控制台输出
        print("no")
        pass

# 主程序
if __name__ == "__main__":
    while True:
        time.sleep(1)  # 用较短的间隔时间加速检测
        image_path = "click.jpg"
        check_and_click_image(image_path)
