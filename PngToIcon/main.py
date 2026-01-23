from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # 导入 ttk
import os
import shutil
import subprocess  # 用于打开文件夹
import random

def createicon(pngpath, folder_path):
    # 打开图像（支持各种格式）
    img = Image.open(pngpath)

    # 确保图像是RGBA模式，因为ICO格式可能需要透明度
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # 定义ICO文件所需的标准尺寸
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

    # 遍历尺寸列表，生成并保存每个尺寸的图标
    for size in sizes:
        imgresized = img.resize(size, Image.Resampling.LANCZOS)  # 使用LANCZOS代替ANTIALIAS

        # 构造保存的文件路径，使用尺寸作为文件名后缀
        icon_filename = f"icon_{size[0]}x{size[1]}.ico"
        icopath = os.path.join(folder_path, icon_filename)

        # 保存为ICO文件
        imgresized.save(icopath, format='ICO')

def on_select_image():
    # 打开文件对话框选择图像文件，支持多种格式
    pngpath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpeg;*.jpg;*.bmp;*.gif;*.tiff;*.webp")])
    if pngpath:
        # 显示选中的图片
        img = Image.open(pngpath)
        img.thumbnail((200, 200))  # 缩小显示图像
        img_tk = ImageTk.PhotoImage(img)

        label_image.config(image=img_tk)
        label_image.image = img_tk
        entry_pngpath.delete(0, tk.END)
        entry_pngpath.insert(0, pngpath)

def on_generate_icons():
    pngpath = entry_pngpath.get()
    if not pngpath:
        # 弹窗提醒用户选择图片
        messagebox.showwarning("提示", "请选择图片")
        return

    # 生成一个随机文件夹名称
    folder_name = f"generated_icons_{random.randint(1000, 9999)}"
    folder_path = os.path.join(os.getcwd(), folder_name)

    # 如果文件夹已经存在，则删除并重新创建
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # 删除旧文件夹
    os.makedirs(folder_path)  # 创建新的文件夹

    # 生成所有尺寸的图标并保存
    createicon(pngpath, folder_path)

    # 显示生成的文件夹路径
    label_folder.config(text=f"Icons saved in: {folder_path}")

    # 自动打开文件夹
    if os.name == 'nt':  # Windows
        subprocess.Popen(f'explorer {folder_path}')
    elif os.name == 'posix':  # macOS/Linux
        subprocess.Popen(['open', folder_path])

def on_convert_image():
    pngpath = entry_pngpath.get()
    if not pngpath:
        # 弹窗提醒用户选择图片
        messagebox.showwarning("提示", "请选择图片")
        return

    # 获取用户选择的目标格式
    target_format = format_combobox.get()
    if not target_format:
        # 弹窗提醒用户选择格式
        messagebox.showwarning("提示", "请选择转换格式")
        return

    # 检查目标格式是否为有效的图片格式
    valid_formats = ['PNG', 'JPEG', 'JPG', 'BMP', 'GIF', 'TIFF', 'WEBP']
    if target_format.upper() not in valid_formats:
        messagebox.showwarning("提示", "不支持的目标格式")
        return

    # 创建保存文件夹
    converted_folder = os.path.join(os.getcwd(), "converted")
    if not os.path.exists(converted_folder):
        os.makedirs(converted_folder)

    # 打开选中的图片
    img = Image.open(pngpath)

    # 如果是 PNG 且目标格式是 JPEG 或 JPG，转换为 RGB 模式
    if img.mode == 'RGBA' and target_format.upper() in ['JPEG', 'JPG']:
        img = img.convert('RGB')

    # 获取文件名并去掉扩展名
    base_filename = os.path.basename(pngpath)
    filename_without_ext = os.path.splitext(base_filename)[0]

    # 根据目标格式设置正确的文件扩展名
    if target_format.upper() == 'JPG':
        file_extension = '.jpg'
        target_format = 'JPEG'  # 确保保存为 JPEG 格式
    elif target_format.upper() == 'JPEG':
        file_extension = '.jpeg'
        target_format = 'JPEG'
    else:
        file_extension = f'.{target_format.lower()}'

    # 设置保存的路径和文件名
    converted_file_path = os.path.join(converted_folder, f"{filename_without_ext}{file_extension}")

    # 保存转换后的图片，自动覆盖同名文件
    img.save(converted_file_path, format=target_format.upper())

    # 弹窗提示保存路径
    messagebox.showinfo("保存成功", f"图片已保存到：{converted_file_path}")

def on_convert_all_images():
    pngpath = entry_pngpath.get()
    if not pngpath:
        # 弹窗提醒用户选择图片
        messagebox.showwarning("提示", "请选择图片")
        return

    # 创建保存文件夹
    converted_folder = os.path.join(os.getcwd(), "converted")
    if not os.path.exists(converted_folder):
        os.makedirs(converted_folder)

    # 打开选中的图片
    img = Image.open(pngpath)

    # 如果是 PNG 且目标格式是 JPEG 或 JPG，转换为 RGB 模式
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # 获取文件名并去掉扩展名
    base_filename = os.path.basename(pngpath)
    filename_without_ext = os.path.splitext(base_filename)[0]

    # 定义支持的格式
    formats = ['PNG', 'JPEG', 'JPG', 'BMP', 'GIF', 'TIFF', 'WEBP']

    # 遍历格式并转换保存
    for target_format in formats:
        # 设置扩展名和目标格式
        if target_format == 'JPG':
            file_extension = '.jpg'
            target_format = 'JPEG'  # 确保保存为 JPEG 格式
        elif target_format == 'JPEG':
            file_extension = '.jpeg'
            target_format = 'JPEG'
        else:
            file_extension = f'.{target_format.lower()}'

        # 设置保存路径
        converted_file_path = os.path.join(converted_folder, f"{filename_without_ext}{file_extension}")

        # 保存转换后的图片，自动覆盖同名文件
        img.save(converted_file_path, format=target_format)

    # 弹窗提示保存路径
    messagebox.showinfo("保存成功", f"所有格式的图片已保存到：{converted_folder}")

def on_open_converted_folder():
    converted_folder = os.path.join(os.getcwd(), "converted")
    if os.path.exists(converted_folder):
        # 自动打开转换后的文件夹
        if os.name == 'nt':  # Windows
            subprocess.Popen(f'explorer {converted_folder}')
        elif os.name == 'posix':  # macOS/Linux
            subprocess.Popen(['open', converted_folder])
    else:
        messagebox.showwarning("提示", "没有转换的文件夹")

# 创建主窗口
root = tk.Tk()
root.title("Icon Generator")

root.iconbitmap("icon\\icon_128x128.ico")

# 创建左侧面板
frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT, padx=10, pady=10)

# 添加选择图片按钮
button_select_image = tk.Button(frame_left, text="选择图片", command=on_select_image)
button_select_image.pack()

# 显示选择的图片
label_image = tk.Label(frame_left)
label_image.pack(pady=10)

# 输入框显示图片文件路径
entry_pngpath = tk.Entry(frame_left, width=50)
entry_pngpath.pack()

# 创建右侧面板
frame_right = tk.Frame(root)
frame_right.pack(side=tk.LEFT, padx=10, pady=10)

# 添加生成icon图标的按钮
button_generate_icons = tk.Button(frame_right, text="生成 Icons", command=on_generate_icons)
button_generate_icons.pack()

# 添加转换按钮
label_format = tk.Label(frame_right, text="选择目标格式:")
label_format.pack(pady=5)

# 创建目标格式的下拉框
format_combobox = ttk.Combobox(frame_right, values=['PNG', 'JPEG', 'JPG', 'BMP', 'GIF', 'TIFF', 'WEBP'])
format_combobox.pack()

# 添加转换图片按钮
button_convert_image = tk.Button(frame_right, text="转换图片", command=on_convert_image)
button_convert_image.pack(pady=10)

button_convert_all = tk.Button(frame_right, text="转换为所有格式", command=on_convert_all_images)
button_convert_all.pack()

# 添加打开转换后的文件夹按钮
button_open_converted_folder = tk.Button(frame_right, text="打开转换文件夹", command=on_open_converted_folder)
button_open_converted_folder.pack(pady=10)

# 显示生成文件夹路径
label_folder = tk.Label(frame_right, text="Icons 保存在: ")
label_folder.pack(pady=10)

# 运行应用
root.mainloop()
