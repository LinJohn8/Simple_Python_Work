from PIL import Image
from watermarker.marker import add_mark
import os

def resize_image(input_image_path):
    # 打开8K图片
    img = Image.open(input_image_path)

    # 获取原始文件路径、文件名和扩展名
    dir_name, base_name = os.path.split(input_image_path)
    file_name, file_extension = os.path.splitext(base_name)

    # 定义分辨率和对应的文件名后缀
    resolutions = {
        "8k": (7680, 4320),
        "4k": (3840, 2160),
        "2k": (2560, 1440),
        "1k": (1920, 1080)
    }

    resolutions_1k = {
        "1k": (1920, 1080)
    }

    resized_image_paths = []
    for res_name, res_size in resolutions_1k.items():
        # 调整图片大小
        resized_img = img.resize(res_size, Image.LANCZOS)
        # 生成新的文件名和完整输出路径
        new_file_name = f"{file_name}_{res_name}{file_extension}"
        output_image_path = os.path.join(dir_name, new_file_name)
        # 保存图片
        resized_img.save(output_image_path)
        resized_image_paths.append(output_image_path)

    print("图片调整完成！")
    return resized_image_paths

def add_watermark(input_image_path, watermark_text):
    # 获取原始文件路径、文件名和扩展名
    dir_name, base_name = os.path.split(input_image_path)
    file_name, file_extension = os.path.splitext(base_name)

    # 生成新的文件名和完整输出路径
    new_file_name = f"{file_name}_Watermark{file_extension}"
    output_image_path = os.path.join(dir_name, new_file_name)

    # 添加水印
    add_mark(
        file=input_image_path,  # 原图
        mark=watermark_text,  # 水印文字
        out=output_image_path,  # 生成水印图片后的路径
        color='#FFFFFF',  # 颜色
        size=20,  # 字体大小
        opacity=0.5,  # 透明度
        angle=45,  # 旋转角度
        space=300  # 间隔大小
    )

    print(f"水印已添加，生成的图片路径为: {output_image_path}")


# 调用函数，输入你的8K图片地址 - 生成1k, 2k, 4k图片
input_image_path = 'C:\\Users\\ADMIN\\Desktop\\方块\\奇怪的方块_6.png'
resized_image_paths = resize_image(input_image_path)

# 调用函数，为生成的1k图片添加水印
for resized_image_path in resized_image_paths:
    if '_1k' in resized_image_path:
        # add_watermark(resized_image_path, '@御坂8号')
        print("a")