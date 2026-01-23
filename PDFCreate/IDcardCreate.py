import cv2
import numpy as np
from PIL import Image


def preprocess_id_card(image_path):
    """ 读取身份证图片并裁剪身份证区域 """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 使用边缘检测
    edges = cv2.Canny(gray, 50, 150)

    # 轮廓检测
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 找到最大的矩形轮廓（假设身份证是最大矩形）
    largest_rect = None
    max_area = 0
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4:  # 可能是身份证的四边形
            area = cv2.contourArea(cnt)
            if area > max_area:
                max_area = area
                largest_rect = approx

    # 透视变换矫正身份证
    if largest_rect is not None:
        pts = largest_rect.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # top-left
        rect[2] = pts[np.argmax(s)]  # bottom-right

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # top-right
        rect[3] = pts[np.argmax(diff)]  # bottom-left

        # 计算身份证的尺寸
        (tl, tr, br, bl) = rect
        width = max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl))
        height = max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl))

        dst = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]], dtype="float32")

        # 透视变换
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (int(width), int(height)))

        return Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
    else:
        return Image.open(image_path)  # 无法检测则返回原图


def merge_images_vertically(image_paths):
    """ 将两张身份证图片上下合并 """
    images = [preprocess_id_card(img) for img in image_paths]

    # 统一宽度（取最小的宽度）
    min_width = min(img.width for img in images)
    images = [img.resize((min_width, int(img.height * (min_width / img.width)))) for img in images]

    # 计算合成图的高度
    total_height = sum(img.height for img in images)

    # 创建空白画布
    merged_image = Image.new("RGB", (min_width, total_height))

    # 逐个拼接图片
    y_offset = 0
    for img in images:
        merged_image.paste(img, (0, y_offset))
        y_offset += img.height

    return merged_image


def create_pdf(image_paths, output_pdf):
    """ 生成 PDF，只有一页，上下两张身份证 """
    merged_image = merge_images_vertically(image_paths)
    merged_image.save(output_pdf, "PDF", resolution=100.0)


# 示例：等待用户上传文件后调用
image_paths = ["id1.jpg", "id2.jpg"]  # 替换为实际文件路径
output_pdf = "output.pdf"
create_pdf(image_paths, output_pdf)

print(f"PDF 生成成功：{output_pdf}")
