from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import os
import random

def generate_atmospheric_images(input_path, output_folder, num_variants=5):
    """
    生成具有多种氛围感的图片

    Args:
        input_path (str): 输入图片路径
        output_folder (str): 输出文件夹路径
        num_variants (int): 生成的不同版本数量，默认为5

    Returns:
        None
    """
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 加载图片
    img_pillow = Image.open(input_path)
    img_cv = cv2.imread(input_path)

    # 定义不同的处理方式
    processing_methods = [
        {'brightness': random.uniform(0.8, 1.2), 'contrast': random.uniform(0.8, 1.2), 'color': random.uniform(0.8, 1.2)},
        {'brightness': random.uniform(0.8, 1.2), 'contrast': random.uniform(0.8, 1.2), 'sharpness': random.uniform(0.8, 1.2)},
        {'filter': ImageFilter.BLUR, 'radius': random.uniform(1, 3)},
        {'filter': ImageFilter.CONTOUR},
        {'cv_effect': 'edge_detection'},
        {'cv_effect': 'vignette'}
    ]

    for i in range(num_variants):
        # 随机选择一种处理方式
        method = random.choice(processing_methods)

        # 创建一个副本进行处理
        temp_img = img_pillow.copy()

        # 应用Pillow的增强效果
        if 'brightness' in method or 'contrast' in method or 'color' in method or 'sharpness' in method:
            enhancer = ImageEnhance.Brightness(temp_img)
            temp_img = enhancer.enhance(method.get('brightness', 1))

            enhancer = ImageEnhance.Contrast(temp_img)
            temp_img = enhancer.enhance(method.get('contrast', 1))

            enhancer = ImageEnhance.Color(temp_img)
            temp_img = enhancer.enhance(method.get('color', 1))

            enhancer = ImageEnhance.Sharpness(temp_img)
            temp_img = enhancer.enhance(method.get('sharpness', 1))

        # 应用滤镜效果
        if 'filter' in method:
            if method['filter'] == ImageFilter.BLUR:
                temp_img = temp_img.filter(ImageFilter.GaussianBlur(radius=method['radius']))
            else:
                temp_img = temp_img.filter(method['filter'])

        # 应用OpenCV效果
        if 'cv_effect' in method:
            temp_cv = img_cv.copy()
            if method['cv_effect'] == 'edge_detection':
                gray = cv2.cvtColor(temp_cv, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 100, 200)
                temp_cv = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            elif method['cv_effect'] == 'vignette':
                rows, cols = temp_cv.shape[:2]
                kernel_x = cv2.getGaussianKernel(cols, 200)
                kernel_y = cv2.getGaussianKernel(rows, 200)
                kernel = kernel_x * kernel_y.T
                mask = 255 * kernel / kernel.max()
                vignette = np.empty_like(temp_cv)
                vignette[:, :, 0] = mask
                vignette[:, :, 1] = mask
                vignette[:, :, 2] = mask
                temp_cv = cv2.addWeighted(temp_cv, 0.8, vignette, 0.2, 0)
            temp_pil = Image.fromarray(cv2.cvtColor(temp_cv, cv2.COLOR_BGR2RGB))
            temp_img = temp_pil

        # 处理透明度并确定输出格式
        input_ext = os.path.splitext(input_path)[1].lower()
        if temp_img.mode == 'RGBA':
            # 将RGBA转换为RGB，填充白色背景
            background = Image.new('RGB', temp_img.size, (255, 255, 255))
            background.paste(temp_img, mask=temp_img.split()[-1])
            temp_img = background

        # 根据输入扩展名决定输出格式
        if input_ext in ('.png'):
            output_suffix = '.png'
        elif input_ext in ('.jpg', '.jpeg'):
            output_suffix = '.jpg'
        else:
            output_suffix = '.png'  # 默认使用PNG

        # 更新输出路径
        output_path = os.path.join(output_folder, f"atmospheric_{i+1}{output_suffix}")

        # 保存处理后的图片
        temp_img.save(output_path)

    print(f"成功生成 {num_variants} 张氛围感图片，保存在 {output_folder}")
# 示例用法
generate_atmospheric_images("input.png", "output", num_variants=5)