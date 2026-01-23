import os
import tkinter as tk
from tkinter import messagebox
from qr_generation import create_qr, auto_open_folder

# 批量二维码生成界面
def generate_batch_qr(root):
    batch_window = tk.Toplevel(root)
    batch_window.title("批量生成二维码")

    label_urls = tk.Label(batch_window, text="请输入网址（每个网址换行）：")
    label_urls.pack(pady=10)

    entry_urls = tk.Text(batch_window, width=40, height=10)
    entry_urls.pack(pady=10)

    label_folder_name = tk.Label(batch_window, text="输入文件夹名称：")
    label_folder_name.pack(pady=10)

    entry_folder_name = tk.Entry(batch_window, width=40)
    entry_folder_name.pack(pady=10)

    def on_generate_batch():
        urls = entry_urls.get("1.0", "end-1c").splitlines()
        folder_name = entry_folder_name.get().strip()

        if not folder_name:
            messagebox.showwarning("输入文件夹名称", "请输入文件夹名称！")
            return

        # 如果文件夹已经存在，提示是否覆盖
        folder_path = os.path.join(os.getcwd(), folder_name)
        if os.path.exists(folder_path):
            overwrite = messagebox.askyesno("文件夹已存在", f"文件夹 '{folder_name}' 已存在，是否覆盖？")
            if overwrite:
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    os.remove(file_path)
            else:
                return
        else:
            os.makedirs(folder_path)

        # 生成二维码并保存到指定文件夹
        for idx, url in enumerate(urls, start=1):
            filename = os.path.join(folder_path, f"{idx}.png")
            create_qr(url, filename, False)

        messagebox.showinfo("成功", f"二维码已保存到文件夹 '{folder_name}'")
        auto_open_folder()

    button_generate_batch = tk.Button(batch_window, text="生成批量二维码", command=on_generate_batch)
    button_generate_batch.pack(pady=10)
