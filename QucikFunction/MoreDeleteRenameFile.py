import os
import re

# 指定文件夹路径
folder_path = 'C:\\Users\\xxx\\Desktop\\ChangeFolder'

# 获取文件夹中的所有文件
file_list = os.listdir(folder_path)

# 定义正则表达式模式，匹配以数字开头的部分
pattern = re.compile(r'^\d\d\d\d\d-')

# 遍历文件列表
for file_name in file_list:
    # 检查文件是否是图片文件（可以根据需要扩展支持的图片文件类型）
    if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
        # 使用正则表达式替换文件名
        new_file_name = re.sub(pattern, '', file_name)

        # 构建新的文件路径
        old_file_path = os.path.join(folder_path, file_name)
        new_file_path = os.path.join(folder_path, new_file_name)

        # 重命名文件
        os.rename(old_file_path, new_file_path)
        print(f'Renamed: {file_name} to {new_file_name}')

print("ok")