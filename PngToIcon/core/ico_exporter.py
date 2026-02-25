"""
ICO Exporter Module
Handles Windows ICO file generation
"""

from PIL import Image
import os
from typing import List, Optional


class ICOExporter:
    """Export icons to Windows ICO format"""
    
    # Standard ICO sizes
    ICO_SIZES = [16, 32, 48, 64, 128, 256]
    
    def __init__(self, image_processor):
        """
        Initialize ICO exporter
        
        Args:
            image_processor: ImageProcessor instance with loaded image
        """
        self.image_processor = image_processor
    
    def export(self, output_path: str, mode: str = 'contain',
               padding: float = 0.0, radius: float = 0.0,
               squircle: bool = False) -> bool:
        """
        Export to ICO file
        
        Args:
            output_path: Output file path
            mode: 'cover' or 'contain'
            padding: padding percentage
            radius: corner radius percentage
            squircle: use squircle shape
        
        Returns:
            True if successful
        """
        try:
            # Generate all sizes
            images = []
            for size in self.ICO_SIZES:
                img = self.image_processor.process_image(
                    size, mode, padding, radius, squircle
                )
                images.append(img)
            
            # Save as ICO with multiple sizes
            # ICO format requires the largest image first
            images.reverse()  # Put 256 first
            
            # Save
            images[0].save(
                output_path,
                format='ICO',
                sizes=[(img.width, img.height) for img in images],
                append_images=images[1:]
            )
            
            return True
            
        except Exception as e:
            print(f"Error exporting ICO: {e}")
            return False
    
    def export_png_suite(self, output_dir: str, mode: str = 'contain',
                         padding: float = 0.0, radius: float = 0.0,
                         squircle: bool = False, base_name: str = 'icon') -> bool:
        """
        Export PNG files in all sizes
        
        Args:
            output_dir: Output directory
            mode: 'cover' or 'contain'
            padding: padding percentage
            radius: corner radius percentage
            squircle: use squircle shape
            base_name: base filename
        
        Returns:
            True if successful
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for size in self.ICO_SIZES:
                img = self.image_processor.process_image(
                    size, mode, padding, radius, squircle
                )
                filename = f"{base_name}_{size}x{size}.png"
                filepath = os.path.join(output_dir, filename)
                img.save(filepath, format='PNG')
            
            return True
            
        except Exception as e:
            print(f"Error exporting PNG suite: {e}")
            return False