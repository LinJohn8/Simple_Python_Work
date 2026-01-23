import tkinter as tk
from tkinter import messagebox
from qr_generation import create_qr, auto_open_folder

# 单个二维码生成界面
def generate_single_qr(entry_url, entry_filename, label_result):
    url = entry_url.get()
    filename = entry_filename.get() or "temp"  # 默认文件名为temp

    if url:
        create_qr(url, filename)
        auto_open_folder()
        label_result.config(text=f"二维码已保存为：{filename}.png")
    else:
        messagebox.showwarning("输入网址", "请输入一个有效的网址！")
