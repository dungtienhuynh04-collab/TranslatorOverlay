import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen

class DisplayOverlay(QWidget):
    def __init__(self, parent=None, title_text="Kết Quả Dịch", drag_text="≡  Di chuyển  ≡"):
        super().__init__(parent)
        self.title_text = title_text
        self.drag_text = drag_text
        
        self._dragging = False
        self._resizing = False
        self._drag_pos = QPoint()
        
        self.opacity = 180
        self.overflow_mode = 'scroll' # or 'auto_fit'
        self.current_text = "Đang chờ dịch..."
        
        self.interaction_flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        self.setWindowFlags(self.interaction_flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setMouseTracking(True)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title_text)
        self.setGeometry(100, 300, 500, 150)
        self.setMinimumSize(150, 80)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Background Frame
        self.bg_frame = QFrame(self)
        self.bg_frame.setMouseTracking(True)
        self.bg_layout = QVBoxLayout(self.bg_frame)
        self.bg_layout.setContentsMargins(2, 2, 2, 2)
        self.bg_layout.setSpacing(0)
        self.main_layout.addWidget(self.bg_frame)
        
        self.update_style()
        
        # Top Drag Bar
        self.drag_bar = QFrame()
        self.drag_bar.setFixedHeight(22)
        self.drag_bar.setStyleSheet("background-color: rgba(255, 255, 255, 40); border-top-left-radius: 8px; border-top-right-radius: 8px;")
        drag_layout = QHBoxLayout(self.drag_bar)
        drag_layout.setContentsMargins(10, 0, 10, 0)
        
        self.drag_label = QLabel(self.drag_text)
        self.drag_label.setStyleSheet("color: rgba(255,255,255,200); font-size: 11px; font-weight: bold; border: none; background: transparent;")
        self.drag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drag_layout.addWidget(self.drag_label)
        
        self.bg_layout.addWidget(self.drag_bar)
        
        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 8px; background: rgba(0,0,0,50); }
            QScrollBar::handle:vertical { background: rgba(255,255,255,100); border-radius: 4px; }
        """)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Text Label
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        # Setup initial stylesheet correctly
        self.text_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px; background: transparent; border: none;")
        
        self.scroll_area.setWidget(self.text_label)
        self.bg_layout.addWidget(self.scroll_area)

        # Bottom resize grip indicator
        self.resize_grip = QLabel("◢")
        self.resize_grip.setStyleSheet("color: rgba(255,255,255,150); font-size: 14px; background: transparent; border: none; padding-right: 2px;")
        self.resize_grip.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        # Position slightly offset to right-bottom
        self.bg_layout.addWidget(self.resize_grip, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        # Use a timer to delay fit text otherwise geometries aren't calculated immediately on update
        self._fit_timer = QTimer()
        self._fit_timer.setSingleShot(True)
        self._fit_timer.timeout.connect(self._do_fit_text)

        self.update_text(self.current_text)

    def update_language(self, title_text, drag_text):
        self.title_text = title_text
        self.drag_text = drag_text
        self.setWindowTitle(self.title_text)
        self.drag_label.setText(self.drag_text)

    def update_style(self):
        self.bg_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(0, 0, 0, {self.opacity});
                border-radius: 10px;
                border: 2px solid rgba(255, 255, 255, 80);
            }}
        """)

    def set_opacity(self, opacity: int):
        self.opacity = opacity
        self.update_style()

    def set_overflow_mode(self, mode: str):
        self.overflow_mode = mode
        if mode == 'scroll':
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else: # auto_fit
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.update_text(self.current_text)

    def update_text(self, new_text):
        self.current_text = new_text
        if self.overflow_mode == 'auto_fit':
            self.text_label.setText(new_text)
            self._fit_timer.start(50) # Allow layout to settle before calculating
        else:
            self.text_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px; background: transparent; border: none;")
            self.text_label.setText(new_text)

    def _do_fit_text(self):
        if self.overflow_mode != 'auto_fit':
            return
            
        font_size = 28
        viewport_rect = self.scroll_area.viewport().rect()
        target_width = viewport_rect.width() - 20 # considering 10px padding on each side
        target_height = viewport_rect.height() - 20
        
        if target_width <= 0 or target_height <= 0:
            return

        font = QFont("Arial", font_size, QFont.Weight.Bold)
        while font_size >= 10:
            font.setPointSize(font_size)
            metrics = QFontMetrics(font)
            # Use boundingRect to simulate wrap
            rect = metrics.boundingRect(0, 0, target_width, 10000, 
                                        Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignTop, 
                                        self.current_text)
            
            if rect.height() <= target_height:
                break
            font_size -= 1
            
        self.text_label.setStyleSheet(f"color: white; font-size: {font_size}px; font-weight: bold; padding: 10px; background: transparent; border: none;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.overflow_mode == 'auto_fit':
            self._fit_timer.start(50)

    # Mouse handling for dragging and resizing
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            rect = self.rect()
            # If clicked in bottom right corner
            if event.pos().x() > rect.width() - 25 and event.pos().y() > rect.height() - 25:
                self._resizing = True
                self._drag_pos = event.globalPosition().toPoint()
            # Else if clicked inside drag bar (or top area)
            elif event.pos().y() <= self.drag_bar.height() + 5:
                self._dragging = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._resizing:
            diff = event.globalPosition().toPoint() - self._drag_pos
            self.resize(self.width() + diff.x(), self.height() + diff.y())
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()
        elif self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        else:
            # Custom cursor logic without buttons pressed
            rect = self.rect()
            if event.pos().x() > rect.width() - 25 and event.pos().y() > rect.height() - 25:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            super().mouseMoveEvent(event) # propagate for normal tooltips etc

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._resizing = False
            event.accept()
            
    def set_click_through(self, state: bool):
        flags = self.interaction_flags
        if state:
            flags |= Qt.WindowType.WindowTransparentForInput
        
        self.setWindowFlags(flags)
        if not state:
            self.setMouseTracking(True)
        self.show()
