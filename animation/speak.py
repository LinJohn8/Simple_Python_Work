import tkinter as tk
import time

# 读取txt内容
with open("speech.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 每个窗口尺寸
window_width = 1280
window_height = 800

# 创建Lin窗口
root_lin = tk.Tk()
root_lin.title("Lin")
root_lin.geometry(f"{window_width}x{window_height}+0+0")  # 左边
root_lin.configure(bg="white")
root_lin.overrideredirect(True)  # 去掉边框

text_lin = tk.Text(root_lin, bg="white", fg="black", font=("Arial", 16))
text_lin.pack(expand=True, fill="both")
text_lin.config(state=tk.DISABLED)

# 创建Huhu窗口
root_huhu = tk.Tk()
root_huhu.title("Huhu")
root_huhu.geometry(f"{window_width}x{window_height}+1280+0")  # 右边
root_huhu.configure(bg="white")
root_huhu.overrideredirect(True)

text_huhu = tk.Text(root_huhu, bg="white", fg="black", font=("Arial", 16))
text_huhu.pack(expand=True, fill="both")
text_huhu.config(state=tk.DISABLED)

# 打字机效果
def type_text(text_widget, text, delay=0.05):
    text_widget.config(state=tk.NORMAL)
    for char in text:
        text_widget.insert(tk.END, char)
        text_widget.see(tk.END)
        text_widget.update()
        time.sleep(delay)
    text_widget.insert(tk.END, "\n")
    text_widget.config(state=tk.DISABLED)

# 顺序显示
def start_typing():
    for line in lines:
        line = line.strip()
        if line.startswith("Lin:"):
            type_text(text_lin, line)
        elif line.startswith("Huhu:"):
            type_text(text_huhu, line)

# 异步启动
root_lin.after(100, start_typing)

# 同时运行两个窗口
root_huhu.mainloop()
root_lin.mainloop()
