from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json


def setup_driver():
    """设置 Chrome 驱动"""
    chrome_options = Options()
    # 如果不需要看到浏览器界面，可以取消注释下面这行
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")

    # 设置用户代理
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def chat_with_deepseek_selenium(message="你好"):
    """使用 Selenium 与 DeepSeek 聊天"""
    driver = setup_driver()

    try:
        # 打开 DeepSeek 网站
        print("正在打开 DeepSeek 网站...")
        driver.get("https://chat.deepseek.com/")

        # 等待页面加载
        time.sleep(3)

        # 查找输入框并输入消息
        try:
            # 常见的输入框选择器
            input_selectors = [
                "textarea[placeholder*='输入']",
                "textarea[placeholder*='Message']",
                "input[type='text']",
                "textarea",
                "[contenteditable='true']"
            ]

            input_element = None
            for selector in input_selectors:
                try:
                    input_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue

            if input_element:
                print(f"找到输入框，发送消息: {message}")
                input_element.clear()
                input_element.send_keys(message)

                # 查找发送按钮
                send_selectors = [
                    "button[type='submit']",
                    "button:contains('发送')",
                    "button:contains('Send')",
                    ".send-button",
                    "[data-testid='send-button']"
                ]

                send_button = None
                for selector in send_selectors:
                    try:
                        send_button = driver.find_element(By.CSS_SELECTOR, selector)
                        if send_button.is_enabled():
                            break
                    except:
                        continue

                if send_button:
                    send_button.click()
                    print("消息已发送，等待回复...")

                    # 等待回复
                    time.sleep(5)

                    # 尝试获取回复内容
                    response_selectors = [
                        ".message-content",
                        ".response-text",
                        ".chat-message",
                        "[data-testid='message-content']"
                    ]

                    response_text = ""
                    for selector in response_selectors:
                        try:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                response_text = elements[-1].text  # 获取最后一个消息
                                break
                        except:
                            continue

                    if response_text:
                        print(f"收到回复: {response_text}")
                        return response_text
                    else:
                        print("未找到回复内容")
                        return None
                else:
                    print("未找到发送按钮")
                    return None
            else:
                print("未找到输入框")
                return None

        except Exception as e:
            print(f"操作过程中出错: {e}")
            return None

    finally:
        # 关闭浏览器
        driver.quit()


def intercept_network_requests():
    """拦截网络请求获取 PoW 值"""
    chrome_options = Options()
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # 启用网络日志
    chrome_options.add_argument("--enable-network-service-logging")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 启用网络域
        driver.execute_cdp_cmd("Network.enable", {})

        # 设置请求拦截
        def request_interceptor(request):
            if "chat/completion" in request["request"]["url"]:
                headers = request["request"]["headers"]
                if "x-ds-pow-response" in headers:
                    print(f"捕获到 PoW 值: {headers['x-ds-pow-response']}")
                    return headers["x-ds-pow-response"]
            return None

        driver.get("https://chat.deepseek.com/")
        time.sleep(30)  # 等待用户手动操作

    finally:
        driver.quit()


if __name__ == "__main__":
    print("选择运行模式：")
    print("1. 使用 Selenium 自动聊天")
    print("2. 拦截网络请求获取 PoW 值")

    choice = input("请选择 (1 或 2): ").strip()

    if choice == "1":
        message = input("请输入要发送的消息（默认：你好）: ").strip()
        if not message:
            message = "你好"
        result = chat_with_deepseek_selenium(message)
        if result:
            print(f"\n最终回复: {result}")
    elif choice == "2":
        print("启动浏览器，请手动发送消息以捕获 PoW 值...")
        intercept_network_requests()
    else:
        print("无效选择")

# 安装依赖：
# pip install selenium
# 还需要下载 ChromeDriver 并放在 PATH 中