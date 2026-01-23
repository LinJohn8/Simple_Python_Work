import pyautogui
from pynput import mouse


def on_click(x, y, button, pressed):
    """鼠标点击事件处理"""
    if pressed and button == mouse.Button.left:
        try:
            # 获取鼠标位置的颜色
            screenshot = pyautogui.screenshot()
            rgb = screenshot.getpixel((x, y))

            # RGB转16进制
            hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

            # 打印结果
            print(f"\n点击位置: ({x}, {y})")
            print(f"RGB: {rgb}")
            print(f"十六进制: {hex_color}")
            print("-" * 40)

        except Exception as e:
            print(f"获取颜色时出错: {e}")


def main():
    print("屏幕取色器已启动")
    print("点击屏幕任意位置获取颜色")
    print("按 Ctrl+C 退出程序")
    print("=" * 40)

    # 监听鼠标点击事件
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")