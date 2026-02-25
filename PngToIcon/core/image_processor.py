"""
Image Processor Core Module
Handles image scaling, fitting modes, and rounded corners
"""

from PIL import Image, ImageDraw, ImageFilter, ImageOps
import math
import numpy as np
from typing import Tuple, Optional


class ImageProcessor:
    """Core image processing class for icon generation"""
    
    # Standard icon sizes for preview and export
    ICON_SIZES = [16, 32, 64, 128, 256, 512, 1024]
    
    # macOS iconset sizes for icns
    MACOS_ICONSET_SIZES = [
        (16, 16), (16, 16, 2),      # 16x16@1x, 16x16@2x
        (32, 32), (32, 32, 2),      # 32x32@1x, 32x32@2x
        (128, 128), (128, 128, 2),  # 128x128@1x, 128x128@2x
        (256, 256), (256, 256, 2),  # 256x256@1x, 256x256@2x
        (512, 512), (512, 512, 2),  # 512x512@1x, 512x512@2x
    ]
    
    # Windows ico sizes
    WINDOWS_ICO_SIZES = [16, 32, 48, 64, 128, 256]
    
    def __init__(self):
        self.original_image: Optional[Image.Image] = None
        self.processed_image: Optional[Image.Image] = None
        
    def load_image(self, file_path: str) -> bool:
        """Load an image from file path"""
        try:
            self.original_image = Image.open(file_path)
            if self.original_image.mode != 'RGBA':
                self.original_image = self.original_image.convert('RGBA')
            self.processed_image = self.original_image.copy()
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def get_image_info(self) -> dict:
        """Get basic image information"""
        if not self.original_image:
            return {}
        
        # Check for transparency
        has_transparency = False
        if self.original_image.mode == 'RGBA':
            alpha = self.original_image.getchannel('A')
            min_alpha = alpha.getextrema()[0]
            has_transparency = min_alpha < 255
        
        return {
            'width': self.original_image.width,
            'height': self.original_image.height,
            'mode': self.original_image.mode,
            'has_transparency': has_transparency
        }
    
    def apply_fit_mode(self, mode: str, size: int, padding: float = 0.0) -> Image.Image:
        """
        Apply fit mode to image
        
        Args:
            mode: 'cover' (fill and crop) or 'contain' (fit within)
            size: target size (width and height are equal for icons)
            padding: padding percentage (0-30)
        
        Returns:
            Processed PIL Image
        """
        if not self.original_image:
            return None
        
        img = self.original_image.copy()
        target_size = size
        
        # Calculate padding in pixels
        padding_pixels = int(target_size * (padding / 100.0))
        inner_size = target_size - (padding_pixels * 2)
        
        if mode == 'cover':
            # Fill mode: cover entire canvas, may crop
            img = self._resize_cover(img, inner_size)
        else:
            # Contain mode: fit entirely within canvas
            img = self._resize_contain(img, inner_size)
        
        # Create canvas with padding
        canvas = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
        
        # Center paste
        offset = ((target_size - img.width) // 2, (target_size - img.height) // 2)
        canvas.paste(img, offset, img if img.mode == 'RGBA' else None)
        
        return canvas
    
    def _resize_cover(self, img: Image.Image, size: int) -> Image.Image:
        """Resize image to cover the target size (may crop)"""
        ratio = max(size / img.width, size / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Center crop
        left = (img.width - size) // 2
        top = (img.height - size) // 2
        right = left + size
        bottom = top + size
        
        return img.crop((left, top, right, bottom))
    
    def _resize_contain(self, img: Image.Image, size: int) -> Image.Image:
        """Resize image to fit within target size (may have borders)"""
        ratio = min(size / img.width, size / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        return img.resize(new_size, Image.Resampling.LANCZOS)
    
    def apply_rounded_corners(self, img: Image.Image, radius_percent: float, 
                              squircle: bool = False) -> Image.Image:
        """
        Apply rounded corners to image
        
        Args:
            img: PIL Image to process
            radius_percent: corner radius as percentage (0-30)
            squircle: if True, use macOS-style squircle shape
        
        Returns:
            Image with rounded corners
        """
        if radius_percent <= 0:
            return img
        
        size = img.width
        radius = int(size * (radius_percent / 100.0))
        
        # Create mask
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        
        if squircle:
            # Squircle (superellipse) approximation
            mask = self._create_squircle_mask(size, radius)
        else:
            # Standard rounded rectangle
            draw.rounded_rectangle([(0, 0), (size-1, size-1)], radius=radius, fill=255)
        
        # Apply mask
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        return output
    
    def _create_squircle_mask(self, size: int, radius: int) -> Image.Image:
        """
        Create a squircle (superellipse) mask for macOS-style icons
        Optimized with numpy for better performance
        
        The squircle formula: |x|^n + |y|^n = r^n
        For macOS, n ≈ 5 gives a good approximation
        """
        # Squircle parameter (n=5 is close to macOS style)
        n = 5.0
        
        # Use numpy for fast computation
        # Create coordinate grids
        y_coords, x_coords = np.ogrid[:size, :size]
        
        # Normalize coordinates to [-1, 1]
        center = size / 2
        max_radius = size / 2 - 2  # Small margin
        
        nx = np.abs(x_coords - center) / max_radius
        ny = np.abs(y_coords - center) / max_radius
        
        # Check if inside squircle using vectorized operations
        mask_array = (nx ** n + ny ** n <= 1).astype(np.uint8) * 255
        
        # Convert to PIL Image
        mask = Image.fromarray(mask_array, mode='L')
        
        return mask
    
    def process_image(self, size: int, mode: str = 'contain', 
                      padding: float = 0.0, radius: float = 0.0,
                      squircle: bool = False) -> Image.Image:
        """
        Full image processing pipeline
        
        Args:
            size: target icon size
            mode: 'cover' or 'contain'
            padding: padding percentage (0-30)
            radius: corner radius percentage (0-30)
            squircle: use squircle shape
        
        Returns:
            Fully processed PIL Image
        """
        # Apply fit mode
        img = self.apply_fit_mode(mode, size, padding)
        
        # Apply rounded corners
        if radius > 0:
            img = self.apply_rounded_corners(img, radius, squircle)
        
        return img
    
    def generate_preview_sizes(self, mode: str = 'contain', 
                               padding: float = 0.0, radius: float = 0.0,
                               squircle: bool = False) -> dict:
        """
        Generate all preview sizes
        
        Returns:
            Dictionary mapping size to PIL Image
        """
        previews = {}
        for size in self.ICON_SIZES:
            previews[size] = self.process_image(size, mode, padding, radius, squircle)
        return previews