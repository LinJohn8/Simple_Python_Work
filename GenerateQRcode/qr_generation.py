import qrcode
import os
import subprocess


# 自动打开文件夹
def auto_open_folder():
    folder_path = os.path.abspath(os.getcwd())  # 获取当前文件夹路径
    if os.name == 'nt':  # Windows
        subprocess.Popen(f'explorer {folder_path}')
    elif os.name == 'posix':  # macOS/Linux
        subprocess.Popen(['open', folder_path])


# 创建二维码图像
def create_qr(data, filename="temp", show_image=True):
    qr = qrcode.QRCode(
        version=1,  # 控制二维码的大小，1是最小的
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 错误修正级别
        box_size=10,  # 每个小格子的像素大小
        border=4,  # 边框的格子宽度
    )
    qr.add_data(data)
    qr.make(fit=True)

    # 创建二维码图像
    img = qr.make_image(fill='black', back_color='white')

    # 保存二维码图像
    img.save(f"{filename}.png")
    if show_image:
        img.show()
