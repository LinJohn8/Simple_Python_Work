import json
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import math
import requests


# 批量获取文章信息并保存到excel
class GetInformationToExcel:
    def __init__(self, username, cookies, Referer, page, size, filename):
        self.username = username
        self.cookies = cookies
        self.Referer = Referer
        self.size = size
        self.filename = filename
        self.page = page

    # 发送HTTP GET请求到CSDN的API，获取文章列表
    def get_articles(self):
        url = "https://blog.csdn.net/community/home-api/v1/get-business-list"
        params = {
            "page": {self.page},
            "size": {self.size},
            "businessType": "blog",
            "username": {self.username}
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Cookie': self.cookies,
            'Referer': self.Referer
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('list', [])
        except requests.exceptions.HTTPError as e:
            print(f"HTTP错误: {e.response.status_code} {e.response.reason}")
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
        except json.JSONDecodeError:
            print("解析JSON失败")
        return []

    # 将文章列表转换为Pandas DataFrame,选择并重命名必要的列。
    def export_to_excel(self):
        df = pd.DataFrame(self.get_articles())
        df = df[['title', 'url', 'postTime', 'viewCount', 'collectCount', 'diggCount', 'commentCount']]
        df.columns = ['文章标题', 'URL', '发布时间', '阅读量', '收藏量', '点赞量', '评论量']
        wb = Workbook()
        sheet = wb.active
        for r in dataframe_to_rows(df, index=False, header=True):
            sheet.append(r)
        for column in sheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 5)
            sheet.column_dimensions[column[0].column_letter].width = adjusted_width
        # Save the workbook
        wb.save(self.filename)


# 获取每篇文章的质量分，并将分数写入到Excel文件中
class GetArticleScores:
    def __init__(self, filepath):
        self.filepath = filepath

    # 发送HTTP POST请求到一个API，获取文章的质量分。
    @staticmethod
    def get_article_score(article_url):
        url = "https://bizapi.csdn.net/trends/api/v1/get-article-score"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "X-Ca-Key": "203930474",
            "X-Ca-Nonce": "b35e1821-05c2-458d-adae-3b720bb15fdf",
            "X-Ca-Signature": "gjeSiKTRCh8aDv0UwThIVRITc/JtGJkgkZoLVeA6sWo=",
            "X-Ca-Signature-Headers": "x-ca-key,x-ca-nonce",
            "X-Ca-Signed-Content-Type": "multipart/form-data",
        }
        data = {"url": article_url}
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()  # This will raise an error for bad responses
            return response.json().get('data', {}).get('score', 'Score not found')
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return "Error fetching score"

    def get_scores_from_excel(self):
        """读取Excel文件，获取文章URL列表。
            对每个URL调用 get_article_score 方法，获取分数列表。
            返回分数列表。"""
        df = pd.read_excel(self.filepath)
        urls = df['URL'].tolist()
        scores = [self.get_article_score(url) for url in urls]
        return scores

    def write_scores_to_excel(self):
        """读取Excel文件到DataFrame。
            将获取的分数添加到DataFrame中。
            将更新后的DataFrame保存回Excel文件。"""
        df = pd.read_excel(self.filepath)
        df['质量分'] = self.get_scores_from_excel()
        df.to_excel(self.filepath, index=False)


if __name__ == '__main__':
    # 请填写:已发文章总数量,cookies,你的首页Referer，你的id：CSDNid
    total = 145
    cookies = 'uuid_tt_dd=10'  # Simplified for brevity
    Referer = 'https://blog.csdn.net/q244645787'
    CSDNid = 'q244645787'
    # 下面是计算和获取
    t_index = math.ceil(total / 100) + 1  # 向上取整，半闭半开区间，开区间+1。
    for index in range(1, t_index):  # 文章总数
        filename = "score" + str(index) + ".xlsx"
        exporter_excel = GetInformationToExcel(CSDNid, cookies, Referer, index, 100, filename)  # Replace with your username
        exporter_excel.export_to_excel()
        article_score = GetArticleScores(filename)
        article_score.write_scores_to_excel()

    print("获取完成")
