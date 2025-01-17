from PIL import Image

# 读取原始图片
img = Image.open("image.png")

# 创建一个空的图像列表
frames = []

# 生成旋转帧，每隔30度旋转一次，共12帧
for angle in range(0, 360, 30):
    # 旋转图片，expand=True确保旋转后图片不会被裁剪
    rotated_img = img.rotate(angle, expand=True)
    # 将旋转后的图片添加到帧列表中
    frames.append(rotated_img)

# 保存为GIF图
# duration=100表示每帧显示100毫秒，loop=0表示无限循环
frames[0].save("animated_image.gif", save_all=True, append_images=frames[1:], duration=100, loop=0)
