import sys
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QPen

class CaptureOverlay(QWidget):
    geometry_changed = pyqtSignal(tuple) # Emits (x, y, width, height)

    def __init__(self, parent=None, title_text="Khu Vực Chụp", instruction_text="📷 Kéo thanh này để di chuyển - Kéo các góc vuông để Crop"):
        super().__init__(parent)
        self.title_text = title_text
        self.instruction_text = instruction_text
        self.init_ui()
        self._dragging = False
        self._resizing = False
        self._resize_edge = None
        self._drag_pos = QPoint()
        self.RESIZE_MARGIN = 15

    def init_ui(self):
        # Make the window frameless, always on top, and behave like a tool window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        
        # Make the window background transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setWindowTitle(self.title_text)
        self.setGeometry(100, 100, 400, 150)
        self.setMinimumSize(60, 60)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Inner clear area (pure transparent black)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        
        # Border
        # Draw elegant solid border instead of dashed green
        pen = QPen(QColor(255, 255, 255, 220), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        # Inset slightly so it renders fully inside widget
        content_rect = self.rect().adjusted(2, 2, -3, -3)
        painter.drawRect(content_rect)
        
        # Draw corner and edge handles (little white squares)
        handle_color = QColor(255, 255, 255, 255)
        h_size = 10
        w, h = self.width(), self.height()
        
        handles = [
            QRect(0, 0, h_size, h_size), # Top Left
            QRect(w//2 - h_size//2, 0, h_size, h_size), # Top Center
            QRect(w - h_size, 0, h_size, h_size), # Top Right
            QRect(0, h//2 - h_size//2, h_size, h_size), # Left Center
            QRect(w - h_size, h//2 - h_size//2, h_size, h_size), # Right Center
            QRect(0, h - h_size, h_size, h_size), # Bottom Left
            QRect(w//2 - h_size//2, h - h_size, h_size, h_size), # Bottom Center
            QRect(w - h_size, h - h_size, h_size, h_size), # Bottom Right
        ]
        
        for r in handles:
            painter.fillRect(r, handle_color)
        
        # Add a sleek instruction text label centered horizontally at the top
        painter.setPen(QPen(QColor(255, 255, 255, 200)))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        
        text = self.instruction_text
        text_rect = painter.fontMetrics().boundingRect(content_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, text)
        # Fill a subtle background behind the text
        painter.fillRect(text_rect.adjusted(-5, -2, 5, 2), QColor(0, 0, 0, 150))
        painter.drawText(content_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, text)

    # --- Mouse Events for Dragging and Resizing ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._get_resize_edge(event.pos())
            if edge:
                self._resizing = True
                self._resize_edge = edge
            else:
                self._dragging = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            self._emit_geometry()
            event.accept()
        elif self._resizing:
            self._handle_resize(event.globalPosition().toPoint())
            self._emit_geometry()
            event.accept()
        else:
            # Update cursor based on hover position
            edge = self._get_resize_edge(event.pos())
            if edge in ('top_left', 'bottom_right'):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif edge in ('top_right', 'bottom_left'):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif edge in ('top', 'bottom'):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            elif edge in ('left', 'right'):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.SizeAllCursor) # For moving

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._resizing = False
            self._resize_edge = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self._emit_geometry()
            event.accept()

    def _get_resize_edge(self, pos):
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        m = self.RESIZE_MARGIN

        is_left = x < m
        is_right = x > w - m
        is_top = y < m
        is_bottom = y > h - m

        if is_top and is_left: return 'top_left'
        if is_top and is_right: return 'top_right'
        if is_bottom and is_left: return 'bottom_left'
        if is_bottom and is_right: return 'bottom_right'
        if is_left: return 'left'
        if is_right: return 'right'
        if is_top: return 'top'
        if is_bottom: return 'bottom'
        return None

    def _handle_resize(self, global_pos):
        if not self._resize_edge:
            return
        geom = self.frameGeometry()
        if 'left' in self._resize_edge:
            geom.setLeft(global_pos.x())
        if 'right' in self._resize_edge:
            geom.setRight(global_pos.x())
        if 'top' in self._resize_edge:
            geom.setTop(global_pos.y())
        if 'bottom' in self._resize_edge:
            geom.setBottom(global_pos.y())
        
        # Enforce minimum size logic
        if geom.width() < self.minimumWidth():
            if 'left' in self._resize_edge:
                geom.setLeft(geom.right() - self.minimumWidth())
            else:
                geom.setRight(geom.left() + self.minimumWidth())
                
        if geom.height() < self.minimumHeight():
            if 'top' in self._resize_edge:
                geom.setTop(geom.bottom() - self.minimumHeight())
            else:
                geom.setBottom(geom.top() + self.minimumHeight())
                
        self.setGeometry(geom)

    def _emit_geometry(self):
        geom = self.geometry()
        self.geometry_changed.emit((geom.x(), geom.y(), geom.width(), geom.height()))
