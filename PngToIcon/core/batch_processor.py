"""
Batch Processor Module
Handles batch processing of multiple PNG files
"""

import os
import zipfile
from typing import List, Callable, Optional
from PIL import Image

from .image_processor import ImageProcessor
from .ico_exporter import ICOExporter
from .icns_exporter import ICNSExporter


class BatchProcessor:
    """Process multiple PNG files with the same settings"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.ico_exporter = ICOExporter(self.image_processor)
        self.icns_exporter = ICNSExporter(self.image_processor)
        
    def get_png_files(self, folder_path: str) -> List[str]:
        """
        Get all PNG files in a folder
        
        Args:
            folder_path: Path to folder
        
        Returns:
            List of PNG file paths
        """
        png_files = []
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.lower().endswith('.png'):
                    png_files.append(os.path.join(folder_path, filename))
        return sorted(png_files)
    
    def process_folder(self, folder_path: str, output_dir: str,
                       mode: str = 'contain', padding: float = 0.0,
                       radius: float = 0.0, squircle: bool = False,
                       export_formats: List[str] = None,
                       progress_callback: Callable[[int, int, str], None] = None) -> dict:
        """
        Process all PNG files in a folder
        
        Args:
            folder_path: Input folder with PNG files
            output_dir: Output directory
            mode: 'cover' or 'contain'
            padding: padding percentage
            radius: corner radius percentage
            squircle: use squircle shape
            export_formats: list of formats ['icns', 'ico', 'png']
            progress_callback: callback(current, total, filename)
        
        Returns:
            Dictionary with results
        """
        if export_formats is None:
            export_formats = ['ico']
        
        png_files = self.get_png_files(folder_path)
        total = len(png_files)
        results = {
            'success': [],
            'failed': [],
            'total': total
        }
        
        if total == 0:
            return results
        
        os.makedirs(output_dir, exist_ok=True)
        
        for i, png_path in enumerate(png_files):
            filename = os.path.basename(png_path)
            base_name = os.path.splitext(filename)[0]
            
            if progress_callback:
                progress_callback(i + 1, total, filename)
            
            try:
                # Load image
                if not self.image_processor.load_image(png_path):
                    results['failed'].append({'file': filename, 'error': 'Failed to load'})
                    continue
                
                # Create output subfolder for this file
                file_output_dir = os.path.join(output_dir, base_name)
                os.makedirs(file_output_dir, exist_ok=True)
                
                # Export in selected formats
                for fmt in export_formats:
                    if fmt == 'ico':
                        ico_path = os.path.join(file_output_dir, f"{base_name}.ico")
                        self.ico_exporter.export(ico_path, mode, padding, radius, squircle)
                    
                    elif fmt == 'icns':
                        icns_path = os.path.join(file_output_dir, f"{base_name}.icns")
                        self.icns_exporter.export(icns_path, mode, padding, radius, squircle)
                    
                    elif fmt == 'png':
                        png_dir = os.path.join(file_output_dir, 'png_suite')
                        self.icns_exporter.export_png_suite(
                            png_dir, mode, padding, radius, squircle, base_name
                        )
                
                results['success'].append(filename)
                
            except Exception as e:
                results['failed'].append({'file': filename, 'error': str(e)})
        
        return results
    
    def create_zip_archive(self, source_dir: str, zip_path: str) -> bool:
        """
        Create a ZIP archive of the output
        
        Args:
            source_dir: Directory to zip
            zip_path: Output ZIP file path
        
        Returns:
            True if successful
        """
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
            return True
        except Exception as e:
            print(f"Error creating ZIP: {e}")
            return False


def export_png_suite_zip(image_processor: ImageProcessor, output_path: str,
                         mode: str = 'contain', padding: float = 0.0,
                         radius: float = 0.0, squircle: bool = False,
                         base_name: str = 'icon') -> bool:
    """
    Export PNG suite as a ZIP file
    
    Args:
        image_processor: ImageProcessor instance with loaded image
        output_path: Output ZIP file path
        mode: 'cover' or 'contain'
        padding: padding percentage
        radius: corner radius percentage
        squircle: use squircle shape
        base_name: base filename
    
    Returns:
        True if successful
    """
    import tempfile
    
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export all PNG sizes
            sizes = [16, 32, 64, 128, 256, 512, 1024]
            
            for size in sizes:
                img = image_processor.process_image(
                    size, mode, padding, radius, squircle
                )
                filename = f"{base_name}_{size}x{size}.png"
                filepath = os.path.join(temp_dir, filename)
                img.save(filepath, format='PNG')
            
            # Create ZIP
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for size in sizes:
                    filename = f"{base_name}_{size}x{size}.png"
                    filepath = os.path.join(temp_dir, filename)
                    zipf.write(filepath, filename)
            
            return True
            
    except Exception as e:
        print(f"Error exporting PNG suite ZIP: {e}")
        return False