from PIL import Image, ImageDraw, ImageFont

# 用于构建输出文本的ASCII字符
ASCII_CHARS = "@%#*+=-:. "

# 根据新的宽度调整图像大小
def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio * 0.55)  # 调整比例以适应字符高度
    resized_image = image.resize((new_width, new_height))
    return resized_image

# 将每个像素转换为灰度
def grayify(image):
    grayscale_image = image.convert("L")
    return grayscale_image

# 将像素转换为ASCII字符字符串
def pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = ""
    for pixel in pixels:
        ascii_str += ASCII_CHARS[pixel // 32]
    return ascii_str

# 从ASCII字符串创建图像
def ascii_to_image(ascii_str, img_width, char_size, output_image_path):
    lines = ascii_str.split('\n')

    # 加载字体
    font = ImageFont.load_default()

    char_width, char_height = char_size

    # 计算新图像尺寸
    img_height = char_height * len(lines)

    # 创建一个带有白色背景的新图像
    new_image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(new_image)

    # 将ASCII字符绘制到图像上
    x = 0
    y = 0
    for line in lines:
        draw.text((x, y), line, fill="black", font=font)
        y += char_height

    # 保存图像
    new_image.save(output_image_path)

# 将图像转换为ASCII并保存为图像
def image_to_ascii_image(image_path, output_image_path, new_width=100):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"无法打开图像文件 {image_path}. {e}")
        return

    resized_image = resize_image(image, new_width)
    gray_image = grayify(resized_image)

    ascii_str = pixels_to_ascii(gray_image)
    ascii_str_with_newlines = "\n".join([ascii_str[i:i + new_width] for i in range(0, len(ascii_str), new_width)])
    img_width = new_width

    # 测量字符大小
    test_image = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(test_image)
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), "@", font=font)
    char_width = bbox[2] - bbox[0]
    char_height = bbox[3] - bbox[1]

    # 计算最终图像的宽度
    final_img_width = char_width * new_width
    final_img_height = char_height * len(ascii_str_with_newlines.split('\n'))

    ascii_to_image(ascii_str_with_newlines, final_img_width, (char_width, char_height), output_image_path)

# 使用示例
image_path = "C:\\Users\\ADMIN\\Desktop\\test.png"
output_image_path = "C:\\Users\\ADMIN\\Desktop\\ascii_image.png"
image_to_ascii_image(image_path, output_image_path)
print(f"ASCII图像保存在 {output_image_path}")
