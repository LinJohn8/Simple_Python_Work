"""
Configuration Manager Module
Handles application settings, language selection, and user preferences
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Manage application configuration and settings"""
    
    DEFAULT_CONFIG = {
        'language': 'zh',  # 'zh' or 'en'
        'default_export_dir': '',  # Default export directory
        'last_export_dir': '',  # Last used export directory
        'default_format': 'ico',  # Default export format
        'remember_settings': True,  # Remember last used settings
        'last_settings': {
            'mode': 'contain',
            'padding': 0,
            'radius': 0,
            'squircle': False
        }
    }
    
    # Language translations
    TRANSLATIONS = {
        'zh': {
            # App title
            'app_title': 'PNG 转 Icon 工具',
            
            # Drop area
            'drop_hint': '拖拽 PNG 图片到这里\n或点击选择文件',
            'select_png': '选择 PNG 图片',
            'png_files': 'PNG 文件 (*.png)',
            
            # Image info
            'no_image': '未选择图片',
            'has_transparency': '✓ 透明通道',
            'no_transparency': '✗ 无透明通道',
            
            # Preview
            'multi_size_preview': '多尺寸预览',
            
            # Control panel
            'fit_mode': '适配模式',
            'mode': '模式:',
            'contain': '适配 (Contain)',
            'cover': '填充 (Cover)',
            'padding': '留白:',
            'corner_settings': '圆角设置',
            'radius': '圆角:',
            'squircle': 'macOS 风格圆角 (Squircle)',
            'export_options': '导出选项',
            'transparent_bg': '透明背景',
            
            # Export panel
            'export': '导出',
            'export_icns': '导出 ICNS (macOS)',
            'export_ico': '导出 ICO (Windows)',
            'export_png_suite': '导出 PNG 套件 (ZIP)',
            'batch_export': '批量导出',
            
            # File dialogs
            'save_icns': '保存 ICNS',
            'save_ico': '保存 ICO',
            'save_png_suite': '保存 PNG 套件',
            'icns_files': 'ICNS 文件 (*.icns)',
            'ico_files': 'ICO 文件 (*.ico)',
            'zip_files': 'ZIP 文件 (*.zip)',
            'select_png_folder': '选择包含 PNG 图片的文件夹',
            'select_output_folder': '选择输出文件夹',
            
            # Messages
            'ready': '准备就绪',
            'loaded': '已加载',
            'exporting_icns': '正在导出 ICNS...',
            'exporting_ico': '正在导出 ICO...',
            'exporting_png': '正在导出 PNG 套件...',
            'processing': '处理中',
            'batch_complete': '批量处理完成',
            'success': '成功',
            'failed': '失败',
            'failed_files': '失败文件',
            'select_image_first': '请先选择图片',
            'no_png_files': '所选文件夹中没有 PNG 文件',
            'icns_saved': 'ICNS 已保存到',
            'ico_saved': 'ICO 已保存到',
            'png_saved': 'PNG 套件已保存到',
            'export_failed': '导出失败',
            'export_error': '导出错误',
            'load_error': '无法加载图片',
            'select_png_only': '请选择 PNG 格式的图片',
            
            # Settings dialog
            'settings': '设置',
            'language': '语言:',
            'chinese': '中文',
            'english': 'English',
            'default_export_path': '默认导出路径:',
            'browse': '浏览...',
            'save': '保存',
            'cancel': '取消',
            
            # Menu
            'file': '文件',
            'edit': '编辑',
            'help': '帮助',
        },
        'en': {
            # App title
            'app_title': 'PNG to Icon Converter',
            
            # Drop area
            'drop_hint': 'Drag PNG image here\nor click to select',
            'select_png': 'Select PNG Image',
            'png_files': 'PNG Files (*.png)',
            
            # Image info
            'no_image': 'No image selected',
            'has_transparency': '✓ Has transparency',
            'no_transparency': '✗ No transparency',
            
            # Preview
            'multi_size_preview': 'Multi-size Preview',
            
            # Control panel
            'fit_mode': 'Fit Mode',
            'mode': 'Mode:',
            'contain': 'Contain',
            'cover': 'Cover',
            'padding': 'Padding:',
            'corner_settings': 'Corner Settings',
            'radius': 'Radius:',
            'squircle': 'macOS Style (Squircle)',
            'export_options': 'Export Options',
            'transparent_bg': 'Transparent Background',
            
            # Export panel
            'export': 'Export',
            'export_icns': 'Export ICNS (macOS)',
            'export_ico': 'Export ICO (Windows)',
            'export_png_suite': 'Export PNG Suite (ZIP)',
            'batch_export': 'Batch Export',
            
            # File dialogs
            'save_icns': 'Save ICNS',
            'save_ico': 'Save ICO',
            'save_png_suite': 'Save PNG Suite',
            'icns_files': 'ICNS Files (*.icns)',
            'ico_files': 'ICO Files (*.ico)',
            'zip_files': 'ZIP Files (*.zip)',
            'select_png_folder': 'Select folder with PNG images',
            'select_output_folder': 'Select output folder',
            
            # Messages
            'ready': 'Ready',
            'loaded': 'Loaded',
            'exporting_icns': 'Exporting ICNS...',
            'exporting_ico': 'Exporting ICO...',
            'exporting_png': 'Exporting PNG suite...',
            'processing': 'Processing',
            'batch_complete': 'Batch processing complete',
            'success': 'Success',
            'failed': 'Failed',
            'failed_files': 'Failed files',
            'select_image_first': 'Please select an image first',
            'no_png_files': 'No PNG files in selected folder',
            'icns_saved': 'ICNS saved to',
            'ico_saved': 'ICO saved to',
            'png_saved': 'PNG suite saved to',
            'export_failed': 'Export failed',
            'export_error': 'Export error',
            'load_error': 'Cannot load image',
            'select_png_only': 'Please select PNG format image',
            
            # Settings dialog
            'settings': 'Settings',
            'language': 'Language:',
            'chinese': '中文',
            'english': 'English',
            'default_export_path': 'Default Export Path:',
            'browse': 'Browse...',
            'save': 'Save',
            'cancel': 'Cancel',
            
            # Menu
            'file': 'File',
            'edit': 'Edit',
            'help': 'Help',
        }
    }
    
    def __init__(self, config_dir: str = None):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Directory to store config file, defaults to app directory
        """
        if config_dir is None:
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.config_path = os.path.join(config_dir, 'config.json')
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged = self.DEFAULT_CONFIG.copy()
                    merged.update(config)
                    return merged
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def get_language(self) -> str:
        """Get current language"""
        return self.config.get('language', 'zh')
    
    def set_language(self, language: str):
        """Set language"""
        if language in ['zh', 'en']:
            self.config['language'] = language
            self.save_config()
    
    def get_translation(self, key: str) -> str:
        """Get translated string for current language"""
        lang = self.get_language()
        translations = self.TRANSLATIONS.get(lang, self.TRANSLATIONS['zh'])
        return translations.get(key, key)
    
    def get_all_translations(self) -> Dict[str, str]:
        """Get all translations for current language"""
        lang = self.get_language()
        return self.TRANSLATIONS.get(lang, self.TRANSLATIONS['zh'])
    
    def get_default_export_dir(self) -> str:
        """Get default export directory"""
        return self.config.get('default_export_dir', '')
    
    def set_default_export_dir(self, path: str):
        """Set default export directory"""
        self.config['default_export_dir'] = path
        self.save_config()
    
    def get_last_settings(self) -> Dict[str, Any]:
        """Get last used settings"""
        return self.config.get('last_settings', {})
    
    def save_last_settings(self, settings: Dict[str, Any]):
        """Save last used settings"""
        if self.config.get('remember_settings', True):
            self.config['last_settings'] = settings
            self.save_config()