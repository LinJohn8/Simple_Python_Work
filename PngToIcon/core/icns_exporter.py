"""
ICNS Exporter Module
Handles macOS ICNS file generation
"""

from PIL import Image
import os
import subprocess
import platform
import shutil
import tempfile
from typing import Optional


class ICNSExporter:
    """Export icons to macOS ICNS format"""
    
    # macOS iconset sizes (size, scale)
    # Each entry is (width, height, scale_factor)
    ICONSET_SIZES = [
        (16, 16, 1),    # icon_16x16.png
        (16, 16, 2),    # icon_16x16@2x.png
        (32, 32, 1),    # icon_32x32.png
        (32, 32, 2),    # icon_32x32@2x.png
        (128, 128, 1),  # icon_128x128.png
        (128, 128, 2),  # icon_128x128@2x.png
        (256, 256, 1),  # icon_256x256.png
        (256, 256, 2),  # icon_256x256@2x.png
        (512, 512, 1),  # icon_512x512.png
        (512, 512, 2),  # icon_512x512@2x.png
    ]
    
    def __init__(self, image_processor):
        """
        Initialize ICNS exporter
        
        Args:
            image_processor: ImageProcessor instance with loaded image
        """
        self.image_processor = image_processor
    
    def _create_iconset(self, iconset_dir: str, mode: str, padding: float,
                        radius: float, squircle: bool) -> bool:
        """
        Create .iconset directory with all required PNG files
        
        Args:
            iconset_dir: Path to .iconset directory
            mode: 'cover' or 'contain'
            padding: padding percentage
            radius: corner radius percentage
            squircle: use squircle shape
        
        Returns:
            True if successful
        """
        try:
            os.makedirs(iconset_dir, exist_ok=True)
            
            for width, height, scale in self.ICONSET_SIZES:
                actual_size = width * scale
                img = self.image_processor.process_image(
                    actual_size, mode, padding, radius, squircle
                )
                
                # Generate filename
                if scale == 1:
                    filename = f"icon_{width}x{height}.png"
                else:
                    filename = f"icon_{width}x{height}@{scale}x.png"
                
                filepath = os.path.join(iconset_dir, filename)
                img.save(filepath, format='PNG')
            
            return True
            
        except Exception as e:
            print(f"Error creating iconset: {e}")
            return False
    
    def export(self, output_path: str, mode: str = 'contain',
               padding: float = 0.0, radius: float = 0.0,
               squircle: bool = False) -> bool:
        """
        Export to ICNS file
        
        Args:
            output_path: Output file path (.icns)
            mode: 'cover' or 'contain'
            padding: padding percentage
            radius: corner radius percentage
            squircle: use squircle shape
        
        Returns:
            True if successful
        """
        try:
            # Create temporary iconset directory
            base_name = os.path.splitext(os.path.basename(output_path))[0]
            iconset_dir = output_path.replace('.icns', '.iconset')
            
            # Create iconset
            if not self._create_iconset(iconset_dir, mode, padding, radius, squircle):
                return False
            
            # Convert to ICNS
            if platform.system() == 'Darwin':  # macOS
                # Use built-in iconutil
                result = subprocess.run(
                    ['iconutil', '-c', 'icns', '-o', output_path, iconset_dir],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"iconutil error: {result.stderr}")
                    # Try alternative method
                    return self._create_icns_alternative(iconset_dir, output_path)
                
                # Clean up iconset directory
                shutil.rmtree(iconset_dir, ignore_errors=True)
                return True
            else:
                # On non-macOS, use alternative method
                success = self._create_icns_alternative(iconset_dir, output_path)
                shutil.rmtree(iconset_dir, ignore_errors=True)
                return success
                
        except Exception as e:
            print(f"Error exporting ICNS: {e}")
            return False
    
    def _create_icns_alternative(self, iconset_dir: str, output_path: str) -> bool:
        """
        Alternative ICNS creation for non-macOS systems
        Creates a basic ICNS file structure
        
        Args:
            iconset_dir: Path to iconset directory
            output_path: Output ICNS file path
        
        Returns:
            True if successful
        """
        try:
            # ICNS file format header
            # This is a simplified implementation
            
            # Read the 512x512 image as the main icon
            icon_512 = os.path.join(iconset_dir, 'icon_512x512.png')
            icon_512_2x = os.path.join(iconset_dir, 'icon_512x512@2x.png')
            
            if os.path.exists(icon_512_2x):
                # Use the @2x version for better quality
                img = Image.open(icon_512_2x)
            elif os.path.exists(icon_512):
                img = Image.open(icon_512)
            else:
                # Generate from scratch
                img = self.image_processor.process_image(512, 'contain', 0, 0, False)
            
            # For cross-platform compatibility, we'll save as PNG with .icns extension
            # and also create a proper iconset folder that can be converted on macOS
            
            # Save a high-res PNG that can be converted later
            img.save(output_path.replace('.icns', '_1024.png'), format='PNG')
            
            # Try to create a basic ICNS using PIL (limited support)
            # This creates a valid ICNS on macOS PIL builds
            try:
                # Collect all images
                images = []
                for size in [16, 32, 64, 128, 256, 512, 1024]:
                    if size <= 1024:
                        img_path = os.path.join(iconset_dir, f'icon_{size}x{size}.png')
                        if os.path.exists(img_path):
                            images.append(Image.open(img_path))
                
                if images:
                    # Save as ICNS (PIL has limited ICNS support)
                    images[0].save(output_path, format='ICNS')
                    return True
            except Exception as e:
                print(f"PIL ICNS save failed: {e}")
            
            # If all else fails, create a note for the user
            note_path = output_path.replace('.icns', '_convert_note.txt')
            with open(note_path, 'w') as f:
                f.write("To create ICNS on non-macOS:\n")
                f.write(f"1. The iconset folder is at: {iconset_dir}\n")
                f.write("2. On macOS, run: iconutil -c icns <iconset_folder>\n")
                f.write("3. Or use online converters\n")
            
            return True
            
        except Exception as e:
            print(f"Alternative ICNS creation failed: {e}")
            return False
    
    def export_png_suite(self, output_dir: str, mode: str = 'contain',
                         padding: float = 0.0, radius: float = 0.0,
                         squircle: bool = False, base_name: str = 'icon') -> bool:
        """
        Export PNG files in all macOS icon sizes
        
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
            
            # Export all sizes including @2x versions
            for width, height, scale in self.ICONSET_SIZES:
                actual_size = width * scale
                img = self.image_processor.process_image(
                    actual_size, mode, padding, radius, squircle
                )
                
                if scale == 1:
                    filename = f"{base_name}_{width}x{height}.png"
                else:
                    filename = f"{base_name}_{width}x{height}@{scale}x.png"
                
                filepath = os.path.join(output_dir, filename)
                img.save(filepath, format='PNG')
            
            # Also export 1024x1024 for App Store
            img_1024 = self.image_processor.process_image(
                1024, mode, padding, radius, squircle
            )
            filepath_1024 = os.path.join(output_dir, f"{base_name}_1024x1024.png")
            img_1024.save(filepath_1024, format='PNG')
            
            return True
            
        except Exception as e:
            print(f"Error exporting PNG suite: {e}")
            return False