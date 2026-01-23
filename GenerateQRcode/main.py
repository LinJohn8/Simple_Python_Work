import tkinter as tk
from qr_generation import create_qr
from single_qr_generation import generate_single_qr
from batch_qr_generation import generate_batch_qr

# 主界面
def main():
    root = tk.Tk()
    root.title("网址二维码生成器")
    root.iconbitmap("icon_128x128.ico")

    # 输入网址
    label_url = tk.Label(root, text="请输入网址：")
    label_url.pack(pady=10)

    entry_url = tk.Entry(root, width=50)
    entry_url.pack(pady=10)

    # 输入二维码图片名字
    label_filename = tk.Label(root, text="请输入二维码图片名字（默认 'temp'）：")
    label_filename.pack(pady=10)

    entry_filename = tk.Entry(root, width=50)
    entry_filename.pack(pady=10)

    # 结果显示
    label_result = tk.Label(root, text="")
    label_result.pack(pady=10)

    # 生成单个二维码按钮
    button_generate_single = tk.Button(root, text="生成二维码", command=lambda: generate_single_qr(entry_url, entry_filename, label_result))
    button_generate_single.pack(pady=10)

    # 批量生成二维码按钮
    button_generate_batch = tk.Button(root, text="批量生成二维码", command=lambda: generate_batch_qr(root))
    button_generate_batch.pack(pady=10)

    # 运行主界面
    root.mainloop()


if __name__ == "__main__":
    main()
