"""
Main Window UI
PySide6-based main application window
"""

import sys
import os
from PIL import Image
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QComboBox, QCheckBox, QGroupBox,
    QFileDialog, QMessageBox, QProgressBar, QFrame, QScrollArea,
    QSizePolicy, QSplitter, QDialog, QSpinBox, QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QMimeData
from PySide6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent, QPainter, QColor, QAction

from core.image_processor import ImageProcessor
from core.ico_exporter import ICOExporter
from core.icns_exporter import ICNSExporter
from core.batch_processor import BatchProcessor, export_png_suite_zip
from core.config_manager import ConfigManager
from utils.checkerboard import create_preview_pixmap, composite_on_checkerboard, pil_to_qpixmap


class SettingsDialog(QDialog):
    """Settings dialog for language and export path"""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.translations = config_manager.get_all_translations()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(self.translations.get('settings', 'Settings'))
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItem('中文', 'zh')
        self.language_combo.addItem('English', 'en')
        # Set current language
        current_lang = self.config_manager.get_language()
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        form_layout.addRow(self.translations.get('language', 'Language:'), self.language_combo)
        
        # Default export path
        path_layout = QHBoxLayout()
        self.path_edit = QLabel()
        self.path_edit.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        current_path = self.config_manager.get_default_export_dir()
        self.path_edit.setText(current_path if current_path else self.translations.get('not_set', '(未设置)'))
        self.path_edit.setWordWrap(True)
        
        self.browse_btn = QPushButton(self.translations.get('browse', 'Browse...'))
        self.browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(self.path_edit, stretch=1)
        path_layout.addWidget(self.browse_btn)
        form_layout.addRow(self.translations.get('default_export_path', 'Default Export Path:'), path_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(
            self, self.translations.get('select_output_folder', 'Select output folder')
        )
        if path:
            self.path_edit.setText(path)
            
    def _save_settings(self):
        new_lang = self.language_combo.currentData()
        self.config_manager.set_language(new_lang)
        self.config_manager.set_default_export_dir(self.path_edit.text())
        self.accept()


class DropArea(QLabel):
    """Custom widget for drag and drop area"""
    
    image_dropped = Signal(str)  # Signal emitted when image is dropped
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.translations = config_manager.get_all_translations()
        self.setMinimumSize(300, 200)
        self.setMaximumSize(400, 300)
        self.setAlignment(Qt.AlignCenter)
        self.setText(self.translations.get('drop_hint', 'Drag PNG image here\nor click to select'))
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f5f5f5;
                color: #666;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #4a9eff;
                background-color: #e8f4ff;
            }
        """)
        self.setAcceptDrops(True)
        
    def update_translations(self):
        self.translations = self.config_manager.get_all_translations()
        self.setText(self.translations.get('drop_hint', 'Drag PNG image here\nor click to select'))
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #4a9eff;
                    border-radius: 10px;
                    background-color: #d0e8ff;
                    color: #333;
                    font-size: 14px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f5f5f5;
                color: #666;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #4a9eff;
                background-color: #e8f4ff;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith('.png'):
                self.image_dropped.emit(file_path)
            else:
                # Show error message
                pass
        
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f5f5f5;
                color: #666;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #4a9eff;
                background-color: #e8f4ff;
            }
        """)
    
    def mousePressEvent(self, event):
        # Click to select file
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.translations.get('select_png', 'Select PNG Image'), 
            "", self.translations.get('png_files', 'PNG Files (*.png)')
        )
        if file_path:
            self.image_dropped.emit(file_path)


class ImagePreviewLabel(QLabel):
    """Label to display the loaded image with checkerboard background"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setMaximumSize(300, 300)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
            }
        """)
        self.setText("")
        
    def set_image(self, pil_image: Image.Image):
        """Set image from PIL Image"""
        if pil_image:
            # Resize to fit
            display_size = min(self.width() - 10, self.height() - 10, 280)
            ratio = display_size / max(pil_image.width, pil_image.height)
            new_size = (int(pil_image.width * ratio), int(pil_image.height * ratio))
            
            # Composite on checkerboard
            if pil_image.mode == 'RGBA':
                display_img = composite_on_checkerboard(pil_image, 8)
            else:
                display_img = pil_image.convert('RGB')
            
            display_img = display_img.resize(new_size, Image.Resampling.LANCZOS)
            pixmap = pil_to_qpixmap(display_img)
            self.setPixmap(pixmap)
        else:
            self.clear()
            self.setText("")


class PreviewWidget(QLabel):
    """Widget for displaying a single preview size"""
    
    def __init__(self, size: int, parent=None):
        super().__init__(parent)
        self.icon_size = size
        self.display_size = min(size, 80)  # Max display size
        self.setMinimumSize(self.display_size + 20, self.display_size + 40)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: transparent;")
        self.setText(f"{size}x{size}")
        
    def set_preview_image(self, pil_image):
        """Set the preview image from PIL Image"""
        if pil_image:
            # Scale to display size
            ratio = self.display_size / max(pil_image.width, pil_image.height)
            new_size = (int(pil_image.width * ratio), int(pil_image.height * ratio))
            
            # Composite on checkerboard
            if pil_image.mode == 'RGBA':
                display_img = composite_on_checkerboard(pil_image, 5)
            else:
                display_img = pil_image.convert('RGB')
            
            display_img = display_img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to QPixmap
            pixmap = pil_to_qpixmap(display_img)
            self.setPixmap(pixmap)


class PreviewPanel(QWidget):
    """Panel showing multiple size previews"""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.preview_widgets = {}
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        translations = self.config_manager.get_all_translations()
        title = QLabel(translations.get('multi_size_preview', 'Multi-size Preview'))
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Preview grid
        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setSpacing(10)
        
        # Create preview widgets for each size
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        for size in sizes:
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)
            container_layout.setSpacing(5)
            
            # Preview widget
            preview = PreviewWidget(size)
            self.preview_widgets[size] = preview
            container_layout.addWidget(preview, alignment=Qt.AlignCenter)
            
            # Size label
            size_label = QLabel(f"{size}x{size}")
            size_label.setAlignment(Qt.AlignCenter)
            size_label.setStyleSheet("font-size: 11px; color: #666;")
            container_layout.addWidget(size_label)
            
            grid_layout.addWidget(container)
        
        grid_layout.addStretch()
        layout.addWidget(grid_widget)
        layout.addStretch()
        
    def update_previews(self, previews: dict):
        """Update all preview images"""
        for size, pil_image in previews.items():
            if size in self.preview_widgets:
                self.preview_widgets[size].set_preview_image(pil_image)


class ControlPanel(QWidget):
    """Panel with editing controls"""
    
    settings_changed = Signal()  # Emitted when any setting changes
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        translations = self.config_manager.get_all_translations()
        
        # === Fit Mode Group ===
        fit_group = QGroupBox(translations.get('fit_mode', 'Fit Mode'))
        fit_layout = QVBoxLayout(fit_group)
        
        # Mode combo
        mode_layout = QHBoxLayout()
        mode_label = QLabel(translations.get('mode', 'Mode:'))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([translations.get('contain', 'Contain'), translations.get('cover', 'Cover')])
        self.mode_combo.currentIndexChanged.connect(self._on_settings_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        fit_layout.addLayout(mode_layout)
        
        # Padding slider
        padding_layout = QHBoxLayout()
        padding_label = QLabel(translations.get('padding', 'Padding:'))
        self.padding_slider = QSlider(Qt.Horizontal)
        self.padding_slider.setRange(0, 30)
        self.padding_slider.setValue(0)
        self.padding_slider.valueChanged.connect(self._on_settings_changed)
        self.padding_value = QLabel("0%")
        self.padding_slider.valueChanged.connect(
            lambda v: self.padding_value.setText(f"{v}%")
        )
        padding_layout.addWidget(padding_label)
        padding_layout.addWidget(self.padding_slider)
        padding_layout.addWidget(self.padding_value)
        fit_layout.addLayout(padding_layout)
        
        layout.addWidget(fit_group)
        
        # === Corner Radius Group ===
        corner_group = QGroupBox(translations.get('corner_settings', 'Corner Settings'))
        corner_layout = QVBoxLayout(corner_group)
        
        # Radius slider
        radius_layout = QHBoxLayout()
        radius_label = QLabel(translations.get('radius', 'Radius:'))
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setRange(0, 30)
        self.radius_slider.setValue(0)
        self.radius_slider.valueChanged.connect(self._on_settings_changed)
        self.radius_value = QLabel("0%")
        self.radius_slider.valueChanged.connect(
            lambda v: self.radius_value.setText(f"{v}%")
        )
        radius_layout.addWidget(radius_label)
        radius_layout.addWidget(self.radius_slider)
        radius_layout.addWidget(self.radius_value)
        corner_layout.addLayout(radius_layout)
        
        # Squircle checkbox
        self.squircle_check = QCheckBox(translations.get('squircle', 'macOS Style (Squircle)'))
        self.squircle_check.stateChanged.connect(self._on_settings_changed)
        corner_layout.addWidget(self.squircle_check)
        
        layout.addWidget(corner_group)
        
        # === Export Options Group ===
        export_group = QGroupBox(translations.get('export_options', 'Export Options'))
        export_layout = QVBoxLayout(export_group)
        
        # Background option
        self.transparent_check = QCheckBox(translations.get('transparent_bg', 'Transparent Background'))
        self.transparent_check.setChecked(True)
        export_layout.addWidget(self.transparent_check)
        
        layout.addWidget(export_group)
        
        layout.addStretch()
        
    def _on_settings_changed(self):
        self.settings_changed.emit()
    
    def get_settings(self) -> dict:
        """Get current settings as dictionary"""
        return {
            'mode': 'contain' if self.mode_combo.currentIndex() == 0 else 'cover',
            'padding': self.padding_slider.value(),
            'radius': self.radius_slider.value(),
            'squircle': self.squircle_check.isChecked(),
            'transparent': self.transparent_check.isChecked()
        }
    
    def set_settings(self, settings: dict):
        """Set settings from dictionary"""
        if 'mode' in settings:
            self.mode_combo.setCurrentIndex(0 if settings['mode'] == 'contain' else 1)
        if 'padding' in settings:
            self.padding_slider.setValue(settings['padding'])
        if 'radius' in settings:
            self.radius_slider.setValue(settings['radius'])
        if 'squircle' in settings:
            self.squircle_check.setChecked(settings['squircle'])


class ExportPanel(QWidget):
    """Panel with export buttons"""
    
    export_icns = Signal(str)  # output path
    export_ico = Signal(str)   # output path
    export_png = Signal(str)   # output path
    batch_export = Signal()    # batch export signal
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        translations = self.config_manager.get_all_translations()
        
        # Title
        title = QLabel(translations.get('export', 'Export'))
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Export buttons
        btn_style = """
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """
        
        # macOS ICNS button
        self.btn_icns = QPushButton("🍎 macOS: 导出 .icns")
        self.btn_icns.setStyleSheet(btn_style + "background-color: #007AFF; color: white;")
        self.btn_icns.clicked.connect(self._on_export_icns)
        layout.addWidget(self.btn_icns)
        
        # Windows ICO button
        self.btn_ico = QPushButton("🪟 Windows: 导出 .ico")
        self.btn_ico.setStyleSheet(btn_style + "background-color: #00A4EF; color: white;")
        self.btn_ico.clicked.connect(self._on_export_ico)
        layout.addWidget(self.btn_ico)
        
        # PNG Suite button
        self.btn_png = QPushButton("📦 PNG套件: 导出多尺寸PNG (ZIP)")
        self.btn_png.setStyleSheet(btn_style + "background-color: #34C759; color: white;")
        self.btn_png.clicked.connect(self._on_export_png)
        layout.addWidget(self.btn_png)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ddd;")
        layout.addWidget(separator)
        
        # Batch export button
        self.btn_batch = QPushButton("📁 " + translations.get('batch_export', 'Batch Export'))
        self.btn_batch.setStyleSheet(btn_style + "background-color: #FF9500; color: white;")
        self.btn_batch.clicked.connect(self._on_batch_export)
        layout.addWidget(self.btn_batch)
        
        layout.addStretch()
    
    def _on_export_icns(self):
        translations = self.config_manager.get_all_translations()
        default_dir = self.config_manager.get_default_export_dir()
        path, _ = QFileDialog.getSaveFileName(
            self, translations.get('save_icns', 'Save ICNS'), 
            os.path.join(default_dir, 'icon.icns') if default_dir else 'icon.icns',
            translations.get('icns_files', 'ICNS Files (*.icns)')
        )
        if path:
            self.export_icns.emit(path)
    
    def _on_export_ico(self):
        translations = self.config_manager.get_all_translations()
        default_dir = self.config_manager.get_default_export_dir()
        path, _ = QFileDialog.getSaveFileName(
            self, translations.get('save_ico', 'Save ICO'),
            os.path.join(default_dir, 'icon.ico') if default_dir else 'icon.ico',
            translations.get('ico_files', 'ICO Files (*.ico)')
        )
        if path:
            self.export_ico.emit(path)
    
    def _on_export_png(self):
        translations = self.config_manager.get_all_translations()
        default_dir = self.config_manager.get_default_export_dir()
        path, _ = QFileDialog.getSaveFileName(
            self, translations.get('save_png_suite', 'Save PNG Suite'),
            os.path.join(default_dir, 'icon_png_suite.zip') if default_dir else 'icon_png_suite.zip',
            translations.get('zip_files', 'ZIP Files (*.zip)')
        )
        if path:
            self.export_png.emit(path)
    
    def _on_batch_export(self):
        self.batch_export.emit()


class ImageInfoWidget(QWidget):
    """Widget showing image information"""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        translations = self.config_manager.get_all_translations()
        
        self.filename_label = QLabel(translations.get('no_image', 'No image selected'))
        self.filename_label.setStyleSheet("font-weight: bold; color: #333;")
        
        self.size_label = QLabel("")
        self.size_label.setStyleSheet("color: #666;")
        
        self.transparency_label = QLabel("")
        self.transparency_label.setStyleSheet("color: #666;")
        
        layout.addWidget(self.filename_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.size_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.transparency_label)
        layout.addStretch()
        
    def update_info(self, filename: str, width: int, height: int, has_transparency: bool):
        translations = self.config_manager.get_all_translations()
        self.filename_label.setText(os.path.basename(filename))
        self.size_label.setText(f"{width} x {height}")
        self.transparency_label.setText(
            translations.get('has_transparency', '✓ Has transparency') if has_transparency 
            else translations.get('no_transparency', '✗ No transparency')
        )


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        
        # Initialize processors
        self.image_processor = ImageProcessor()
        self.ico_exporter = ICOExporter(self.image_processor)
        self.icns_exporter = ICNSExporter(self.image_processor)
        self.batch_processor = BatchProcessor()
        
        # Current file
        self.current_file = None
        
        self.setup_ui()
        self.connect_signals()
        self.apply_translations()
        
        # Load last settings
        last_settings = self.config_manager.get_last_settings()
        if last_settings:
            self.control_panel.set_settings(last_settings)
        
    def setup_ui(self):
        translations = self.config_manager.get_all_translations()
        self.setWindowTitle(translations.get('app_title', 'PNG to Icon Converter'))
        self.setMinimumSize(1100, 650)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # === Top: Import Area ===
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        
        # Drop area
        self.drop_area = DropArea(self.config_manager, self)
        top_layout.addWidget(self.drop_area)
        
        # Image preview
        self.image_preview = ImagePreviewLabel(self)
        top_layout.addWidget(self.image_preview)
        
        # Image info
        self.image_info = ImageInfoWidget(self.config_manager)
        top_layout.addWidget(self.image_info)
        top_layout.addStretch()
        
        main_layout.addWidget(top_widget)
        
        # === Middle: Controls + Preview ===
        middle_widget = QWidget()
        middle_layout = QHBoxLayout(middle_widget)
        middle_layout.setSpacing(20)
        
        # Left: Control panel
        self.control_panel = ControlPanel(self.config_manager)
        self.control_panel.setMaximumWidth(300)
        middle_layout.addWidget(self.control_panel)
        
        # Center: Preview panel
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.preview_panel = PreviewPanel(self.config_manager)
        scroll.setWidget(self.preview_panel)
        scroll.setMinimumHeight(200)
        middle_layout.addWidget(scroll, stretch=1)
        
        # Right: Export panel
        self.export_panel = ExportPanel(self.config_manager)
        self.export_panel.setMaximumWidth(250)
        middle_layout.addWidget(self.export_panel)
        
        main_layout.addWidget(middle_widget, stretch=1)
        
        # === Bottom: Progress bar ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status bar
        self.statusBar().showMessage(translations.get('ready', 'Ready'))
        
    def _create_menu_bar(self):
        translations = self.config_manager.get_all_translations()
        
        # File menu
        file_menu = self.menuBar().addMenu(translations.get('file', 'File'))
        
        # Settings action
        settings_action = QAction(translations.get('settings', 'Settings'), self)
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
    def _show_settings(self):
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            # Apply new translations
            self.apply_translations()
            
    def apply_translations(self):
        """Apply translations to all UI elements"""
        translations = self.config_manager.get_all_translations()
        
        # Update window title
        self.setWindowTitle(translations.get('app_title', 'PNG to Icon Converter'))
        
        # Update status bar
        self.statusBar().showMessage(translations.get('ready', 'Ready'))
        
        # Update drop area
        self.drop_area.update_translations()
        
        # Update menu bar
        self.menuBar().clear()
        self._create_menu_bar()
        
    def connect_signals(self):
        # Drop area
        self.drop_area.image_dropped.connect(self.load_image)
        
        # Control panel
        self.control_panel.settings_changed.connect(self.update_preview)
        
        # Export panel
        self.export_panel.export_icns.connect(self.export_icns)
        self.export_panel.export_ico.connect(self.export_ico)
        self.export_panel.export_png.connect(self.export_png_suite)
        self.export_panel.batch_export.connect(self.batch_export)
        
    def load_image(self, file_path: str):
        """Load an image file"""
        translations = self.config_manager.get_all_translations()
        
        if self.image_processor.load_image(file_path):
            self.current_file = file_path
            
            # Update info
            info = self.image_processor.get_image_info()
            self.image_info.update_info(
                file_path,
                info['width'],
                info['height'],
                info['has_transparency']
            )
            
            # Update image preview
            self.image_preview.set_image(self.image_processor.original_image)
            
            # Update preview
            self.update_preview()
            
            self.statusBar().showMessage(f"{translations.get('loaded', 'Loaded')}: {os.path.basename(file_path)}")
        else:
            QMessageBox.critical(self, translations.get('export_error', 'Error'), 
                               translations.get('load_error', 'Cannot load image'))
    
    def update_preview(self):
        """Update preview images based on current settings"""
        if not self.current_file:
            return
        
        settings = self.control_panel.get_settings()
        
        # Save settings
        self.config_manager.save_last_settings(settings)
        
        # Generate previews
        previews = self.image_processor.generate_preview_sizes(
            mode=settings['mode'],
            padding=settings['padding'],
            radius=settings['radius'],
            squircle=settings['squircle']
        )
        
        # Update preview panel
        self.preview_panel.update_previews(previews)
    
    def export_icns(self, output_path: str):
        """Export to ICNS format"""
        translations = self.config_manager.get_all_translations()
        
        if not self.current_file:
            QMessageBox.warning(self, translations.get('export_error', 'Error'),
                              translations.get('select_image_first', 'Please select an image first'))
            return
        
        settings = self.control_panel.get_settings()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.statusBar().showMessage(translations.get('exporting_icns', 'Exporting ICNS...'))
        
        try:
            if self.icns_exporter.export(
                output_path,
                mode=settings['mode'],
                padding=settings['padding'],
                radius=settings['radius'],
                squircle=settings['squircle']
            ):
                QMessageBox.information(self, translations.get('success', 'Success'),
                                       f"{translations.get('icns_saved', 'ICNS saved to')}: {output_path}")
            else:
                QMessageBox.critical(self, translations.get('export_error', 'Error'),
                                    translations.get('export_failed', 'Export failed'))
        except Exception as e:
            QMessageBox.critical(self, translations.get('export_error', 'Error'),
                               f"{translations.get('export_error', 'Export error')}: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            self.statusBar().showMessage(translations.get('ready', 'Ready'))
    
    def export_ico(self, output_path: str):
        """Export to ICO format"""
        translations = self.config_manager.get_all_translations()
        
        if not self.current_file:
            QMessageBox.warning(self, translations.get('export_error', 'Error'),
                              translations.get('select_image_first', 'Please select an image first'))
            return
        
        settings = self.control_panel.get_settings()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.statusBar().showMessage(translations.get('exporting_ico', 'Exporting ICO...'))
        
        try:
            if self.ico_exporter.export(
                output_path,
                mode=settings['mode'],
                padding=settings['padding'],
                radius=settings['radius'],
                squircle=settings['squircle']
            ):
                QMessageBox.information(self, translations.get('success', 'Success'),
                                       f"{translations.get('ico_saved', 'ICO saved to')}: {output_path}")
            else:
                QMessageBox.critical(self, translations.get('export_error', 'Error'),
                                    translations.get('export_failed', 'Export failed'))
        except Exception as e:
            QMessageBox.critical(self, translations.get('export_error', 'Error'),
                               f"{translations.get('export_error', 'Export error')}: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            self.statusBar().showMessage(translations.get('ready', 'Ready'))
    
    def export_png_suite(self, output_path: str):
        """Export PNG suite as ZIP"""
        translations = self.config_manager.get_all_translations()
        
        if not self.current_file:
            QMessageBox.warning(self, translations.get('export_error', 'Error'),
                              translations.get('select_image_first', 'Please select an image first'))
            return
        
        settings = self.control_panel.get_settings()
        base_name = os.path.splitext(os.path.basename(self.current_file))[0]
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.statusBar().showMessage(translations.get('exporting_png', 'Exporting PNG suite...'))
        
        try:
            if export_png_suite_zip(
                self.image_processor,
                output_path,
                mode=settings['mode'],
                padding=settings['padding'],
                radius=settings['radius'],
                squircle=settings['squircle'],
                base_name=base_name
            ):
                QMessageBox.information(self, translations.get('success', 'Success'),
                                       f"{translations.get('png_saved', 'PNG suite saved to')}: {output_path}")
            else:
                QMessageBox.critical(self, translations.get('export_error', 'Error'),
                                    translations.get('export_failed', 'Export failed'))
        except Exception as e:
            QMessageBox.critical(self, translations.get('export_error', 'Error'),
                               f"{translations.get('export_error', 'Export error')}: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            self.statusBar().showMessage(translations.get('ready', 'Ready'))
    
    def batch_export(self):
        """Batch export multiple files"""
        translations = self.config_manager.get_all_translations()
        
        # Select input folder
        input_folder = QFileDialog.getExistingDirectory(
            self, translations.get('select_png_folder', 'Select folder with PNG images')
        )
        
        if not input_folder:
            return
        
        # Select output folder
        default_dir = self.config_manager.get_default_export_dir()
        output_folder = QFileDialog.getExistingDirectory(
            self, translations.get('select_output_folder', 'Select output folder'),
            default_dir
        )
        
        if not output_folder:
            return
        
        settings = self.control_panel.get_settings()
        
        # Progress callback
        def progress_callback(current, total, filename):
            self.progress_bar.setValue(current)
            self.statusBar().showMessage(
                f"{translations.get('processing', 'Processing')}: {filename} ({current}/{total})"
            )
        
        # Get PNG files first
        png_files = self.batch_processor.get_png_files(input_folder)
        
        if not png_files:
            QMessageBox.warning(self, translations.get('export_error', 'Error'),
                              translations.get('no_png_files', 'No PNG files in selected folder'))
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(png_files))
        self.progress_bar.setValue(0)
        
        # Process
        results = self.batch_processor.process_folder(
            input_folder,
            output_folder,
            mode=settings['mode'],
            padding=settings['padding'],
            radius=settings['radius'],
            squircle=settings['squircle'],
            export_formats=['ico', 'icns', 'png'],
            progress_callback=progress_callback
        )
        
        self.progress_bar.setVisible(False)
        
        # Show results
        msg = f"{translations.get('batch_complete', 'Batch processing complete')}!\n{translations.get('success', 'Success')}: {len(results['success'])}\n{translations.get('failed', 'Failed')}: {len(results['failed'])}"
        if results['failed']:
            msg += f"\n\n{translations.get('failed_files', 'Failed files')}:\n"
            for f in results['failed']:
                msg += f"- {f['file']}: {f['error']}\n"
        
        if results['failed']:
            QMessageBox.warning(self, translations.get('batch_complete', 'Batch Complete'), msg)
        else:
            QMessageBox.information(self, translations.get('success', 'Success'), msg)
        self.statusBar().showMessage(translations.get('ready', 'Ready'))
    
    def closeEvent(self, event):
        """Save settings on close"""
        settings = self.control_panel.get_settings()
        self.config_manager.save_last_settings(settings)
        event.accept()


def run_app():
    """Run the application"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    run_app()