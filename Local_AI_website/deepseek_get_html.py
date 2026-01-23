import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

def clean_dict_latin1(d):
    """清理 dict 中无法用 latin-1 编码的值，防止 requests 报错"""
    cleaned = {}
    for k, v in d.items():
        try:
            v.encode('latin-1')
            cleaned[k] = v
        except UnicodeEncodeError:
            print(f"⚠️ 跳过非法字符字段：{k} -> {v}")
            cleaned[k] = ''.join(c for c in v if ord(c) < 256)
    return cleaned

def fetch_and_save_html(url, headers=None, cookies=None, output_dir="saved_pages"):
    """从指定 URL 抓取网页，格式化 HTML，并保存到本地"""
    print(f"📥 正在抓取：{url}")

    headers = clean_dict_latin1(headers or {})
    cookies = clean_dict_latin1(cookies or {})

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print("❌ 请求失败：", e)
        return

    soup = BeautifulSoup(response.text, "html.parser")
    formatted_html = soup.prettify()

    domain = urlparse(url).netloc.replace(":", "_")
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{domain}.html")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(formatted_html)

    print(f"✅ 网页已保存为：{filename} （状态码：{response.status_code}）")

# ==========================
# ✅ 用法示例
# ==========================
if __name__ == "__main__":
    url = "https://www.sciencedirect.com/journal/information-sciences/vol/719/suppl/C"  # 替换为你想抓取的网页

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    cookies = {
        # 如果有需要可加 cookie，否则留空
    }

    fetch_and_save_html(url, headers=headers, cookies=cookies)
