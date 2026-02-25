"""
PNG to Icon Converter V1
A professional tool for converting PNG images to icon formats

Features:
- F1: One-click import with real-time preview (16/32/64/128/256/512/1024)
- F2: Smart fit modes (Cover/Contain) with padding control
- F3: Rounded corners and macOS-style squircle
- F4: Export to ICNS (macOS), ICO (Windows), PNG suite (ZIP)
- F5: Batch processing for multiple files
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import run_app


if __name__ == '__main__':
    run_app()