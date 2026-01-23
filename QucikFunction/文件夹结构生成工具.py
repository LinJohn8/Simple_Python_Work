import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from pathlib import Path
import os


class FileTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("高级文件结构生成器")
        self.root.geometry("650x750")

        # --- 1. 顶部配置区域 ---
        top_frame = tk.Frame(root, pady=10)
        top_frame.pack(fill="x", padx=15)

        # grid 布局配置
        top_frame.columnconfigure(1, weight=1)

        # [Row 0] 文件夹路径
        tk.Label(top_frame, text="项目路径:").grid(row=0, column=0, sticky="w")
        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(top_frame, textvariable=self.path_var)
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=5)
        tk.Button(top_frame, text="浏览...", command=self.select_directory).grid(row=0, column=2)

        # [Row 1] 包含的文件后缀
        tk.Label(top_frame, text="保留后缀:").grid(row=1, column=0, sticky="w", pady=5)
        self.ext_var = tk.StringVar(value="py cpp h")  # 默认值
        tk.Entry(top_frame, textvariable=self.ext_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        tk.Label(top_frame, text="(留空则显示所有文件)").grid(row=1, column=2, sticky="w")

        # [Row 2] 屏蔽列表 (新增功能)
        tk.Label(top_frame, text="屏蔽文件夹:").grid(row=2, column=0, sticky="w")
        # 默认屏蔽一些常见的垃圾文件夹
        default_ignore = ".git .idea __pycache__ .vscode node_modules .vs"
        self.ignore_var = tk.StringVar(value=default_ignore)
        self.ignore_entry = tk.Entry(top_frame, textvariable=self.ignore_var)
        self.ignore_entry.grid(row=2, column=1, sticky="ew", padx=5)
        tk.Label(top_frame, text="(名称或后缀，空格分隔)").grid(row=2, column=2, sticky="w")

        # --- 2. 按钮区域 ---
        btn_frame = tk.Frame(root, pady=10)
        btn_frame.pack(fill="x", padx=15)

        tk.Button(btn_frame, text="生成结构树", command=self.generate_tree,
                  bg="#007ACC", fg="white", font=("Segoe UI", 10, "bold"), padx=15).pack(side="left")

        tk.Button(btn_frame, text="复制到剪贴板", command=self.copy_to_clipboard, padx=10).pack(side="left", padx=10)

        tk.Button(btn_frame, text="清空", command=lambda: self.text_area.delete("1.0", tk.END), padx=5).pack(side="right")

        # --- 3. 结果显示区域 ---
        # 使用 Consolas 字体保证对齐
        self.text_area = scrolledtext.ScrolledText(root, font=("Consolas", 10))
        self.text_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def select_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def copy_to_clipboard(self):
        content = self.text_area.get("1.0", tk.END)
        if content.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("完成", "已复制到剪贴板！")

    def generate_tree(self):
        root_path = self.path_var.get().strip()
        ext_input = self.ext_var.get().strip()
        ignore_input = self.ignore_var.get().strip()

        if not root_path or not os.path.exists(root_path):
            messagebox.showerror("错误", "请选择有效的文件夹路径。")
            return

        # 1. 处理保留后缀
        target_exts = []
        if ext_input:
            parts = ext_input.split()
            target_exts = [f".{p}" if not p.startswith('.') else p for p in parts]
            target_exts = [p.lower() for p in target_exts]

        # 2. 处理屏蔽列表
        ignore_list = []
        if ignore_input:
            # 全部转小写以便不区分大小写比较
            ignore_list = [x.lower() for x in ignore_input.split()]

        # UI 反馈
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, f"Root: {os.path.basename(root_path)}/\n")

        # 开始生成
        root_obj = Path(root_path)
        tree_str = self._get_tree_string(root_obj, target_exts, ignore_list)

        if not tree_str.strip():
            tree_str = "    (没有找到符合条件的文件)"

        self.text_area.insert(tk.END, tree_str)

    def _should_ignore(self, name, ignore_list):
        """判断文件夹是否应该被忽略"""
        name_lower = name.lower()
        for pattern in ignore_list:
            # 逻辑1: 完全匹配 (例如输入 "temp" 屏蔽 "Temp" 文件夹)
            if name_lower == pattern:
                return True
            # 逻辑2: 后缀匹配 (例如输入 ".bak" 屏蔽 "data.bak" 文件夹)
            # 只有当pattern以点开头，且名字以pattern结尾时才生效
            if pattern.startswith('.') and name_lower.endswith(pattern):
                return True
        return False

    def _get_tree_string(self, directory, target_extensions, ignore_list, prefix=""):
        result = ""
        try:
            # 这里的 iterdir() 结果是无序的，需要收集后排序
            all_items = list(directory.iterdir())
            filtered_entries = []

            for item in all_items:
                # --- 核心过滤逻辑 ---

                # 1. 如果是文件夹
                if item.is_dir():
                    # 检查是否在屏蔽列表中
                    if self._should_ignore(item.name, ignore_list):
                        continue  # 跳过该文件夹
                    filtered_entries.append(item)

                # 2. 如果是文件
                elif item.is_file():
                    # 如果设置了目标后缀，必须匹配
                    if target_extensions:
                        if item.suffix.lower() in target_extensions:
                            filtered_entries.append(item)
                    else:
                        # 没设置后缀默认都要，但也可以选择是否要屏蔽某些文件名(可选功能，目前主要针对文件夹)
                        filtered_entries.append(item)

            # 排序：文件夹和文件混合按名称排序
            filtered_entries.sort(key=lambda x: x.name.lower())

            count = len(filtered_entries)
            for index, entry in enumerate(filtered_entries):
                is_last = (index == count - 1)
                connector = "└── " if is_last else "├── "

                display_name = f"{entry.name}/" if entry.is_dir() else entry.name
                result += f"{prefix}{connector}{display_name}\n"

                if entry.is_dir():
                    extension = "    " if is_last else "│   "
                    result += self._get_tree_string(entry, target_extensions, ignore_list, prefix + extension)

        except PermissionError:
            result += f"{prefix}└── [权限被拒绝]\n"

        return result


if __name__ == "__main__":
    root = tk.Tk()
    # 设置一下高DPI感知，防止在高分屏上模糊（仅Windows有效，非必须）
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = FileTreeApp(root)
    root.mainloop()