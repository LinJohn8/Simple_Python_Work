import requests
import time
import json

# API配置 - 请替换为实际的API信息
url = "https://chat.deepseek.com/api/v0/chat/completion"
x_code = ""  # 请在此处填入实际的x-code
headers = {
    "Authorization": "Bearer YOUR_API_TOKEN_HERE",
    "Content-Type": "application/json",
    "Cookie": "YOUR_COOKIE_HERE",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Origin": "https://chat.deepseek.com",
    "Referer": "https://chat.deepseek.com/a/chat/s/YOUR_CHAT_SESSION_ID",
    "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "x-app-version": "20241129.1",
    "x-client-locale": "zh_CN",
    "x-client-platform": "web",
    "x-client-version": "1.2.0-sse-hint",
    # 关键：添加工作量证明头部
    "x-ds-pow-response": x_code
}

json_data = {
    "chat_session_id": "YOUR_CHAT_SESSION_ID",
    "parent_message_id": None,
    "prompt": "你好",
    "ref_file_ids": []
}

while True:
    response = requests.post(url, headers=headers, json=json_data, stream=True)
    print("状态码:", response.status_code)
    print("响应头:", dict(response.headers))

    if response.status_code == 200:
        print("开始处理流式响应...")
        full_response = ""
        finished = False
        current_event = None

        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line.strip():
                current_event = None
                continue

            print(f"原始行: {raw_line}")  # 调试输出

            if raw_line.startswith("event:"):
                current_event = raw_line[len("event:"):].strip()
                print(f"事件类型: {current_event}")
                continue

            if raw_line.startswith("data:"):
                data_str = raw_line[len("data:"):].strip()
                print(f"数据内容: {data_str}")

                # 检查是否是 [DONE] 标记
                if data_str == "[DONE]":
                    print("收到结束标记")
                    finished = True
                    break

                # 尝试解析JSON
                try:
                    data_json = json.loads(data_str)
                    print(f"解析的JSON: {data_json}")
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}, 数据: {data_str}")
                    continue

                # 检查结束标志
                if current_event == "finish":
                    finished = True

                # 处理数据
                if isinstance(data_json, dict) and "v" in data_json:
                    v = data_json["v"]

                    if isinstance(v, str):
                        full_response += v
                        print(f"累积内容: {full_response}")

                    elif isinstance(v, list):
                        for item in v:
                            if (
                                    isinstance(item, dict)
                                    and item.get("p") == "status"
                                    and item.get("v") == "FINISHED"
                            ):
                                finished = True
                                print("检测到完成状态")

        print("\n完整回答内容:")
        print(full_response)

        if finished:
            break

    elif response.status_code == 429:
        print("请求太频繁，等待10秒后重试...")
        time.sleep(10)
    else:
        print("请求失败，状态码:", response.status_code)
        print("响应内容:", response.text)
        break