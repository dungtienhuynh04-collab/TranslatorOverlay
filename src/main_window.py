import sys
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QGroupBox,
    QTextEdit, QMessageBox, QCheckBox, QTabWidget,
    QPlainTextEdit, QSlider, QApplication
)
from PyQt6.QtCore import Qt, QTime

from src.capture_overlay import CaptureOverlay
from src.display_overlay import DisplayOverlay
from src.llm_service import TranslationService

SETTINGS_FILE = "settings.json"

# UI Translations
I18N = {
    "vi": {
        "title": "Game Translator Overlay - Pro",
        "tab_settings": "Cấu Hình",
        "tab_logs": "Logs (Debug)",
        "group_llm": "Cấu hình LM Studio",
        "lbl_api_url": "URL API:",
        "lbl_model": "Tên Model:",
        "tooltip_model": "Bạn có thể bỏ qua nếu LM Studio chỉ chạy 1 model hiện tại",
        "group_trans": "Cấu hình Dịch thuật",
        "lbl_target_lang": "Ngôn ngữ đích:",
        "lbl_sys_prompt": "System Prompt:",
        "group_display": "Cấu hình Khung Kết Quả",
        "lbl_opacity": "Độ mờ nền:",
        "lbl_overflow": "Xử lý Text dài:",
        "combo_overflow_scroll": "Cuộn bản dịch (Scroll)",
        "combo_overflow_fit": "Tự động thu nhỏ chữ (Auto-fit)",
        "group_app": "Cấu hình Ứng dụng",
        "lbl_theme": "Giao diện (Theme):",
        "combo_theme_dark": "Tối (Dark)",
        "combo_theme_light": "Sáng (Light)",
        "lbl_ui_lang": "Ngôn ngữ UI:",
        "btn_show_capture": "Khung Chụp",
        "btn_hide_capture": "Ẩn K.Chụp",
        "btn_show_display": "Khung Kết Quả",
        "btn_hide_display": "Ẩn K.Kết Quả",
        "check_click_through": "Click xuyên qua Khung KQ",
        "btn_start_trans": "BẮT ĐẦU DỊCH",
        "btn_stop_trans": "DỪNG DỊCH",
        "btn_clear_logs": "Xóa Logs",
        "lbl_status_ready": "Trạng thái: Sẵn sàng",
        "err_no_capture": "Vui lòng mở Khung Chụp trước khi bắt đầu!",
        "err_no_display": "Vui lòng mở Khung Kết Quả trước khi bắt đầu!",
        "msg_start_service": "Đang bắt đầu dịch vụ LLM Service...",
        "msg_stop_service": "Đã dừng dịch.",
        "msg_stop_log": "Đã dừng dịch vụ.",
        "log_loaded": "Đã nạp cài đặt từ settings.json",
        "log_err_load": "Không thể đọc file cài đặt:",
        "log_saved": "Đã lưu cài đặt",
        "log_err_save": "Lỗi khi lưu cài đặt:",
        "status_prefix": "Trạng thái:",
        "title_capture": "Khu Vực Chụp",
        "text_capture_inst": "📷 Kéo thanh này để di chuyển - Kéo các góc vuông để Crop",
        "title_display": "Kết Quả Dịch",
        "text_display_drag": "≡  Di chuyển  ≡"
    },
    "en": {
        "title": "Game Translator Overlay - Pro",
        "tab_settings": "Settings",
        "tab_logs": "Logs (Debug)",
        "group_llm": "LM Studio Config",
        "lbl_api_url": "API URL:",
        "lbl_model": "Model Name:",
        "tooltip_model": "You can leave this blank if LM Studio is only running 1 model",
        "group_trans": "Translation Config",
        "lbl_target_lang": "Target Language:",
        "lbl_sys_prompt": "System Prompt:",
        "group_display": "Display Overlay Config",
        "lbl_opacity": "Background Opacity:",
        "lbl_overflow": "Long Text Handling:",
        "combo_overflow_scroll": "Scroll Translation (Scroll)",
        "combo_overflow_fit": "Auto-fit text size (Auto-fit)",
        "group_app": "App Config",
        "lbl_theme": "UI Theme:",
        "combo_theme_dark": "Dark",
        "combo_theme_light": "Light",
        "lbl_ui_lang": "UI Language:",
        "btn_show_capture": "Capture Box",
        "btn_hide_capture": "Hide Capture",
        "btn_show_display": "Display Box",
        "btn_hide_display": "Hide Display",
        "check_click_through": "Click-through Display Box",
        "btn_start_trans": "START TRANSLATING",
        "btn_stop_trans": "STOP TRANSLATING",
        "btn_clear_logs": "Clear Logs",
        "lbl_status_ready": "Status: Ready",
        "err_no_capture": "Please open the Capture Box before starting!",
        "err_no_display": "Please open the Display Box before starting!",
        "msg_start_service": "Starting LLM Service...",
        "msg_stop_service": "Translation stopped.",
        "msg_stop_log": "Service stopped.",
        "log_loaded": "Settings loaded from settings.json",
        "log_err_load": "Could not read settings file:",
        "log_saved": "Settings saved",
        "log_err_save": "Error saving settings:",
        "status_prefix": "Status:",
        "title_capture": "Capture Region",
        "text_capture_inst": "📷 Drag this bar to move - Drag square corners to Crop",
        "title_display": "Translation Result",
        "text_display_drag": "≡  Move  ≡"
    }
}

THEME_DARK = """
    QWidget { background-color: #2b2b2b; color: #e0e0e0; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }
    QGroupBox { border: 1px solid #444; border-radius: 6px; margin-top: 10px; padding-top: 15px; font-weight: bold; }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
    QLineEdit, QTextEdit, QComboBox, QPlainTextEdit { background-color: #363636; border: 1px solid #555; border-radius: 4px; padding: 4px; color: #fff; }
    QPushButton { background-color: #3a3f44; border: 1px solid #555; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
    QPushButton:hover { background-color: #4a5056; }
    QPushButton:pressed { background-color: #2a2e32; }
    QTabWidget::pane { border: 1px solid #444; border-radius: 4px; top: -1px; }
    QTabBar::tab { background: #363636; border: 1px solid #444; border-bottom-color: #444; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    QTabBar::tab:selected { background: #4a5056; border-bottom-color: #4a5056; }
"""

THEME_LIGHT = """
    QWidget { background-color: #f0f0f0; color: #2b2b2b; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }
    QGroupBox { border: 1px solid #ccc; border-radius: 6px; margin-top: 10px; padding-top: 15px; font-weight: bold; }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
    QLineEdit, QTextEdit, QComboBox, QPlainTextEdit { background-color: #ffffff; border: 1px solid #bbb; border-radius: 4px; padding: 4px; color: #000; }
    QPushButton { background-color: #e0e0e0; border: 1px solid #bbb; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
    QPushButton:hover { background-color: #d0d0d0; }
    QPushButton:pressed { background-color: #c0c0c0; }
    QTabWidget::pane { border: 1px solid #ccc; border-radius: 4px; top: -1px; }
    QTabBar::tab { background: #e0e0e0; border: 1px solid #ccc; border-bottom-color: #ccc; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    QTabBar::tab:selected { background: #ffffff; border-bottom-color: #ffffff; }
"""

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.ui_lang = "vi" # Default
        self.theme = "dark" # Default
        
        # Placeholders for overlays and thread
        self.capture_overlay = None
        self.display_overlay = None
        self.is_translating = False
        self.translation_thread = None
        self.is_force_quit = False

        self.init_ui()
        self.load_settings()
        self.apply_theme()
        self.apply_language()

    def init_ui(self):
        self.resize(550, 600)
        main_layout = QVBoxLayout(self)
        
        # --- TAB WIDGET ---
        self.tabs = QTabWidget()
        self.tab_settings = QWidget()
        self.tab_logs = QWidget()
        
        self.tabs.addTab(self.tab_settings, "Cấu Hình")
        self.tabs.addTab(self.tab_logs, "Logs (Debug)")
        main_layout.addWidget(self.tabs)
        
        # 1. SETUP TAB SETTINGS
        settings_layout = QVBoxLayout(self.tab_settings)

        # --- App Config ---
        self.group_app = QGroupBox("Cấu hình Ứng dụng")
        layout_app = QVBoxLayout(self.group_app)
        
        layout_theme = QHBoxLayout()
        self.lbl_theme = QLabel("Giao diện (Theme):")
        layout_theme.addWidget(self.lbl_theme)
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Tối (Dark)", "Sáng (Light)"])
        self.combo_theme.currentIndexChanged.connect(self.on_theme_changed)
        layout_theme.addWidget(self.combo_theme)
        
        self.lbl_ui_lang = QLabel("Ngôn ngữ UI:")
        layout_theme.addWidget(self.lbl_ui_lang)
        self.combo_ui_lang = QComboBox()
        self.combo_ui_lang.addItems(["Tiếng Việt", "English"])
        self.combo_ui_lang.currentIndexChanged.connect(self.on_lang_changed)
        layout_theme.addWidget(self.combo_ui_lang)
        
        layout_app.addLayout(layout_theme)
        settings_layout.addWidget(self.group_app)

        # --- LM Studio config ---
        self.group_llm = QGroupBox("Cấu hình LM Studio")
        layout_llm = QVBoxLayout(self.group_llm)
        
        layout_url = QHBoxLayout()
        self.lbl_api_url = QLabel("URL API:")
        layout_url.addWidget(self.lbl_api_url)
        self.input_url = QLineEdit()
        layout_url.addWidget(self.input_url)
        layout_llm.addLayout(layout_url)
        
        layout_model = QHBoxLayout()
        self.lbl_model = QLabel("Tên Model:")
        layout_model.addWidget(self.lbl_model)
        self.input_model = QLineEdit()
        layout_model.addWidget(self.input_model)
        layout_llm.addLayout(layout_model)
        
        settings_layout.addWidget(self.group_llm)

        # --- Dịch thuật config ---
        self.group_trans = QGroupBox("Cấu hình Dịch thuật")
        layout_trans = QVBoxLayout(self.group_trans)

        layout_lang = QHBoxLayout()
        self.lbl_target_lang = QLabel("Ngôn ngữ đích:")
        layout_lang.addWidget(self.lbl_target_lang)
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Vietnamese", "English", "Japanese", "Chinese", "Korean"])
        self.combo_lang.setEditable(True)
        layout_lang.addWidget(self.combo_lang)
        layout_trans.addLayout(layout_lang)

        self.lbl_sys_prompt = QLabel("System Prompt:")
        layout_trans.addWidget(self.lbl_sys_prompt)
        self.input_prompt = QTextEdit()
        self.input_prompt.setMaximumHeight(60)
        layout_trans.addWidget(self.input_prompt)

        settings_layout.addWidget(self.group_trans)

        # --- Hiển thị overlay config ---
        self.group_display = QGroupBox("Cấu hình Khung Kết Quả")
        layout_display = QVBoxLayout(self.group_display)
        
        layout_opacity = QHBoxLayout()
        self.lbl_opacity = QLabel("Độ mờ nền:")
        layout_opacity.addWidget(self.lbl_opacity)
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setRange(0, 255)
        self.slider_opacity.setValue(180)
        self.slider_opacity.valueChanged.connect(self.on_opacity_changed)
        layout_opacity.addWidget(self.slider_opacity)
        layout_display.addLayout(layout_opacity)
        
        layout_overflow = QHBoxLayout()
        self.lbl_overflow = QLabel("Xử lý Text dài:")
        layout_overflow.addWidget(self.lbl_overflow)
        self.combo_overflow = QComboBox()
        self.combo_overflow.addItems(["Cuộn bản dịch (Scroll)", "Tự động thu nhỏ chữ (Auto-fit)"])
        self.combo_overflow.currentIndexChanged.connect(self.on_overflow_changed)
        layout_overflow.addWidget(self.combo_overflow)
        layout_display.addLayout(layout_overflow)
        
        settings_layout.addWidget(self.group_display)

        # --- Controls ---
        layout_controls = QHBoxLayout()
        
        self.btn_show_capture = QPushButton("Khung Chụp")
        self.btn_show_capture.clicked.connect(self.toggle_capture_overlay)
        layout_controls.addWidget(self.btn_show_capture)

        self.btn_show_display = QPushButton("Khung Kết Quả")
        self.btn_show_display.clicked.connect(self.toggle_display_overlay)
        layout_controls.addWidget(self.btn_show_display)
        
        self.checkbox_click_through = QCheckBox("Click xuyên qua Khung KQ")
        self.checkbox_click_through.stateChanged.connect(self.toggle_click_through)
        layout_controls.addWidget(self.checkbox_click_through)
        
        settings_layout.addLayout(layout_controls)

        self.btn_start = QPushButton("BẮT ĐẦU DỊCH")
        self.btn_start.setMinimumHeight(45)
        self.btn_start.clicked.connect(self.toggle_translation_loop)
        settings_layout.addWidget(self.btn_start)
        
        # 2. SETUP TAB LOGS
        logs_layout = QVBoxLayout(self.tab_logs)
        
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        # Log box uses custom style to remain readable regardless of main theme
        self.log_box.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; background-color: #1e1e1e; color: #d4d4d4;")
        logs_layout.addWidget(self.log_box)
        
        self.btn_clear_logs = QPushButton("Xóa Logs")
        self.btn_clear_logs.clicked.connect(self.log_box.clear)
        logs_layout.addWidget(self.btn_clear_logs)

        # Status Label on main layout bottom
        self.lbl_status = QLabel("Trạng thái: Sẵn sàng")
        self.lbl_status.setStyleSheet("color: #aaaaaa; font-style: italic; margin-top: 5px;")
        main_layout.addWidget(self.lbl_status)

    def apply_theme(self):
        if self.theme == "dark":
            self.setStyleSheet(THEME_DARK)
            self._update_start_button_style(False)
        else:
            self.setStyleSheet(THEME_LIGHT)
            self._update_start_button_style(False)
            
    def apply_language(self):
        t = I18N.get(self.ui_lang, I18N["vi"])
        
        self.setWindowTitle(t["title"])
        self.tabs.setTabText(0, t["tab_settings"])
        self.tabs.setTabText(1, t["tab_logs"])
        
        self.group_app.setTitle(t["group_app"])
        self.lbl_theme.setText(t["lbl_theme"])
        self.combo_theme.setItemText(0, t["combo_theme_dark"])
        self.combo_theme.setItemText(1, t["combo_theme_light"])
        self.lbl_ui_lang.setText(t["lbl_ui_lang"])
        
        self.group_llm.setTitle(t["group_llm"])
        self.lbl_api_url.setText(t["lbl_api_url"])
        self.lbl_model.setText(t["lbl_model"])
        self.input_model.setToolTip(t["tooltip_model"])
        
        self.group_trans.setTitle(t["group_trans"])
        self.lbl_target_lang.setText(t["lbl_target_lang"])
        self.lbl_sys_prompt.setText(t["lbl_sys_prompt"])
        
        self.group_display.setTitle(t["group_display"])
        self.lbl_opacity.setText(t["lbl_opacity"])
        self.lbl_overflow.setText(t["lbl_overflow"])
        self.combo_overflow.setItemText(0, t["combo_overflow_scroll"])
        self.combo_overflow.setItemText(1, t["combo_overflow_fit"])
        
        # Keep toggle state text correct
        if self.capture_overlay and self.capture_overlay.isVisible():
            self.btn_show_capture.setText(t["btn_hide_capture"])
        else:
            self.btn_show_capture.setText(t["btn_show_capture"])
            
        if self.display_overlay and self.display_overlay.isVisible():
            self.btn_show_display.setText(t["btn_hide_display"])
        else:
            self.btn_show_display.setText(t["btn_show_display"])
            
        self.checkbox_click_through.setText(t["check_click_through"])
        self.btn_clear_logs.setText(t["btn_clear_logs"])
        
        if self.is_translating:
            self.btn_start.setText(t["btn_stop_trans"])
        else:
            self.btn_start.setText(t["btn_start_trans"])
            
    def _update_start_button_style(self, stop_state):
        if stop_state: # Means we should show "Stop Translating" style (RED)
            color = "#d32f2f"
            hover = "#c62828"
        else: # Normal start state (GREEN)
            color = "#2e7d32" if self.theme == "dark" else "#4caf50"
            hover = "#388e3c" if self.theme == "dark" else "#388e3c"
            
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                font-size: 14px; font-weight: bold; background-color: {color}; color: white; border: none; border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
        """)

    def on_theme_changed(self, index):
        self.theme = "dark" if index == 0 else "light"
        self.apply_theme()
        self.save_settings()
        
    def on_lang_changed(self, index):
        self.ui_lang = "vi" if index == 0 else "en"
        self.apply_language()
        self.save_settings()

    def log_message(self, message, is_error=False):
        """Append a message to the logs tab with a timestamp"""
        timestamp = QTime.currentTime().toString("HH:mm:ss")
        if is_error:
            formatted_msg = f"<span style='color: #ff5252;'>[{timestamp}] ERROR: {message}</span>"
        else:
            formatted_msg = f"<span style='color: #81c784;'>[{timestamp}] INFO: {message}</span>"
            
        self.log_box.appendHtml(formatted_msg)

    def load_settings(self):
        """Load settings from JSON file"""
        default_settings = {
            "url": "http://localhost:1234/v1",
            "model": "mistralai/ministral-3-3b",
            "language": "Vietnamese",
            "prompt": "Bạn là một chuyên gia dịch thuật game. Hãy dịch nội dung trong hình ảnh này sang {language}. Chỉ xuất ra câu dịch, không kèm lời giải thích nào khác.",
            "opacity": 180,
            "overflow_mode": 0,
            "theme": 0,
            "ui_lang": 0
        }
        
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    default_settings.update(settings)
                self.log_message(I18N.get(self.ui_lang, I18N["vi"])["log_loaded"])
            except Exception as e:
                self.log_message(f"Load JSON failed: {e}", is_error=True)

        self.input_url.setText(default_settings["url"])
        self.input_model.setText(default_settings["model"])
        self.combo_lang.setCurrentText(default_settings["language"])
        self.input_prompt.setPlainText(default_settings["prompt"])
        self.slider_opacity.setValue(default_settings.get("opacity", 180))
        self.combo_overflow.setCurrentIndex(default_settings.get("overflow_mode", 0))
        
        # Load theme & UI Lang
        self.combo_theme.setCurrentIndex(default_settings.get("theme", 0))
        self.combo_ui_lang.setCurrentIndex(default_settings.get("ui_lang", 0))
        
        self.theme = "dark" if self.combo_theme.currentIndex() == 0 else "light"
        self.ui_lang = "vi" if self.combo_ui_lang.currentIndex() == 0 else "en"

    def save_settings(self):
        """Save settings to JSON file"""
        settings = {
            "url": self.input_url.text(),
            "model": self.input_model.text(),
            "language": self.combo_lang.currentText(),
            "prompt": self.input_prompt.toPlainText(),
            "opacity": self.slider_opacity.value(),
            "overflow_mode": self.combo_overflow.currentIndex(),
            "theme": self.combo_theme.currentIndex(),
            "ui_lang": self.combo_ui_lang.currentIndex()
        }
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            self.log_message(I18N.get(self.ui_lang, I18N["vi"])["log_saved"])
        except Exception as e:
            self.log_message(f"Save JSON failed: {e}", is_error=True)

    def toggle_capture_overlay(self):
        t = I18N.get(self.ui_lang, I18N["vi"])
        if self.capture_overlay is None:
            self.capture_overlay = CaptureOverlay(title_text=t["title_capture"], instruction_text=t["text_capture_inst"])
            self.capture_overlay.geometry_changed.connect(self.on_capture_geometry_changed)
            self.capture_overlay.show()
            self.btn_show_capture.setText(t["btn_hide_capture"])
        else:
            if self.capture_overlay.isVisible():
                self.capture_overlay.hide()
                self.btn_show_capture.setText(t["btn_show_capture"])
            else:
                self.capture_overlay.show()
                self.btn_show_capture.setText(t["btn_hide_capture"])

    def toggle_display_overlay(self):
        t = I18N.get(self.ui_lang, I18N["vi"])
        if self.display_overlay is None:
            self.display_overlay = DisplayOverlay(title_text=t["title_display"], drag_text=t["text_display_drag"])
            self.display_overlay.set_opacity(self.slider_opacity.value())
            self.display_overlay.set_overflow_mode('scroll' if self.combo_overflow.currentIndex() == 0 else 'auto_fit')
            self.display_overlay.show()
            self.btn_show_display.setText(t["btn_hide_display"])
        else:
            if self.display_overlay.isVisible():
                self.display_overlay.hide()
                self.btn_show_display.setText(t["btn_show_display"])
            else:
                self.display_overlay.show()
                self.btn_show_display.setText(t["btn_hide_display"])

    def toggle_click_through(self, state):
        if self.display_overlay:
            self.display_overlay.set_click_through(state == Qt.CheckState.Checked.value)

    def on_opacity_changed(self, value):
        if self.display_overlay:
            self.display_overlay.set_opacity(value)
            
    def on_overflow_changed(self, index):
        if self.display_overlay:
            mode = 'scroll' if index == 0 else 'auto_fit'
            self.display_overlay.set_overflow_mode(mode)

    def on_capture_geometry_changed(self, geom):
        if self.translation_thread and self.translation_thread.is_running:
            self.translation_thread.update_geometry(geom)

    def toggle_translation_loop(self):
        t = I18N.get(self.ui_lang, I18N["vi"])
        
        if not self.is_translating:
            if not self.capture_overlay or not self.capture_overlay.isVisible():
                QMessageBox.warning(self, t["tab_settings"], t["err_no_capture"])
                return
            if not self.display_overlay or not self.display_overlay.isVisible():
                QMessageBox.warning(self, t["tab_settings"], t["err_no_display"])
                return

            self.save_settings()
            
            self.btn_start.setText(t["btn_stop_trans"])
            self._update_start_button_style(stop_state=True)
            self.is_translating = True
            
            geom = self.capture_overlay.geometry()
            capture_geom = (geom.x(), geom.y(), geom.width(), geom.height())
            
            self.translation_thread = TranslationService(
                api_url=self.input_url.text(),
                model_name=self.input_model.text(),
                target_lang=self.combo_lang.currentText(),
                sys_prompt=self.input_prompt.toPlainText(),
                capture_geom=capture_geom
            )
            
            self.translation_thread.translation_result.connect(self.display_overlay.update_text)
            self.translation_thread.error_occurred.connect(self.handle_thread_error)
            self.translation_thread.status_update.connect(self.update_status_bar)
            
            self.log_message(t["msg_start_service"])
            self.translation_thread.start()
        else:
            self.btn_start.setText(t["btn_start_trans"])
            self._update_start_button_style(stop_state=False)
            self.is_translating = True
            
            self.is_translating = False
            self.update_status_bar(t["msg_stop_service"])
            self.log_message(t["msg_stop_log"])
            
            if self.translation_thread:
                self.translation_thread.stop()
                self.translation_thread = None

    def handle_thread_error(self, err_msg):
        self.lbl_status.setText(f"Lỗi/Error: {err_msg}")
        self.log_message(err_msg, is_error=True)
        
    def update_status_bar(self, msg):
        t = I18N.get(self.ui_lang, I18N["vi"])
        self.lbl_status.setText(f"{t['status_prefix']} {msg}")
        # Only log significant status updates
        if "thành công" not in msg.lower() and "phát hiện" not in msg.lower() and "detected" not in msg.lower() and "success" not in msg.lower():
            self.log_message(msg)

    def closeEvent(self, event):
        """Intercept the close event to minimize to system tray instead"""
        if self.is_force_quit:
            # Actually exiting the app
            self.save_settings()
            if self.translation_thread:
                self.translation_thread.stop()
            if self.capture_overlay:
                self.capture_overlay.close()
            if self.display_overlay:
                self.display_overlay.close()
            event.accept()
        else:
            # Minimize to tray
            event.ignore()
            self.hide()
            
    def quit_app(self):
        """Fully quit the app from the system tray"""
        self.is_force_quit = True
        QApplication.quit()
