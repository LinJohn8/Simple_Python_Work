import os
import shutil


def copy_png_files(source_dir, destination_dir):
    # 创建目标文件夹（如果不存在）
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # 遍历源文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # 如果文件扩展名是.png，复制到目标文件夹中
            if file.endswith('.png'):
                source_path = os.path.join(root, file)
                destination_path = os.path.join(destination_dir, file)
                shutil.copy2(source_path, destination_path)


# 指定源文件夹的路径
source_folder = 'path'
# 指定目标文件夹的路径
destination_folder = 'path'

copy_png_files(source_folder, destination_folder)