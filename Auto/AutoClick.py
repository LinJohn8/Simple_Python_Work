import pyautogui
import time

# 指定你要搜索的图片路径
image_path = "red.png"  # 替换成你的图片路径

# 检查屏幕上是否有图片，并点击
def check_and_click_image(image_path):
    try:
        # 查找屏幕上的图像并返回位置
        location = pyautogui.locateOnScreen(image_path, confidence=1)  # 使用较低的confidence提高速度
        if location:
            # 获取图像的中心位置并点击
            center = pyautogui.center(location)
            pyautogui.click(center)
            print(f"已点击图标，位置: {center}")
        else:
            # 如果找不到图像，可以选择不输出任何信息，避免不必要的控制台输出
            pass
    except pyautogui.ImageNotFoundException:
        pass  # 如果图片没有找到，不做任何处理，继续下一次检测

# 主程序
if __name__ == "__main__":
    while True:
        time.sleep(0.1)  # 用较短的间隔时间加速检测
        check_and_click_image(image_path)
