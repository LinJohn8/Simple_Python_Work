"""
Checkerboard Background Generator
Creates transparent checkerboard pattern for preview
"""

from PIL import Image
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt


def create_checkerboard_image(width: int, height: int, square_size: int = 10) -> Image.Image:
    """
    Create a checkerboard pattern image
    
    Args:
        width: Image width
        height: Image height
        square_size: Size of each checkerboard square
    
    Returns:
        PIL Image with checkerboard pattern
    """
    # Light and dark colors for transparency indication
    light_color = (200, 200, 200)  # Light gray
    dark_color = (150, 150, 150)   # Dark gray
    
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            # Determine which color to use
            checker_x = x // square_size
            checker_y = y // square_size
            
            if (checker_x + checker_y) % 2 == 0:
                pixels[x, y] = light_color
            else:
                pixels[x, y] = dark_color
    
    return img


def composite_on_checkerboard(rgba_image: Image.Image, square_size: int = 10) -> Image.Image:
    """
    Composite an RGBA image on a checkerboard background
    
    Args:
        rgba_image: PIL Image with alpha channel
        square_size: Size of each checkerboard square
    
    Returns:
        RGB PIL Image composited on checkerboard
    """
    if rgba_image.mode != 'RGBA':
        rgba_image = rgba_image.convert('RGBA')
    
    # Create checkerboard
    checkerboard = create_checkerboard_image(
        rgba_image.width, rgba_image.height, square_size
    )
    
    # Composite
    checkerboard.paste(rgba_image, (0, 0), rgba_image)
    
    return checkerboard


def pil_to_qpixmap(pil_image: Image.Image) -> QPixmap:
    """
    Convert PIL Image to QPixmap
    
    Args:
        pil_image: PIL Image
    
    Returns:
        QPixmap
    """
    if pil_image.mode == 'RGBA':
        # Convert RGBA to ARGB for Qt
        data = pil_image.tobytes('raw', 'BGRA')
        qimage = QImage(data, pil_image.width, pil_image.height, 
                       pil_image.width * 4, QImage.Format_ARGB32)
    else:
        # RGB
        pil_image = pil_image.convert('RGB')
        data = pil_image.tobytes('raw', 'RGB')
        qimage = QImage(data, pil_image.width, pil_image.height,
                       pil_image.width * 3, QImage.Format_RGB888)
    
    return QPixmap.fromImage(qimage)


def create_preview_pixmap(pil_image: Image.Image, display_size: int, 
                          show_checkerboard: bool = True) -> QPixmap:
    """
    Create a preview pixmap at the specified display size
    
    Args:
        pil_image: PIL Image to preview
        display_size: Maximum display dimension
        show_checkerboard: Whether to show checkerboard for transparency
    
    Returns:
        QPixmap for display
    """
    # Resize for display
    ratio = min(display_size / pil_image.width, display_size / pil_image.height)
    new_size = (int(pil_image.width * ratio), int(pil_image.height * ratio))
    
    # Use high-quality resampling
    display_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Composite on checkerboard if needed
    if show_checkerboard and display_image.mode == 'RGBA':
        display_image = composite_on_checkerboard(display_image)
    
    return pil_to_qpixmap(display_image)