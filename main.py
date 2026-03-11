import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from src.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Keep running when main window is closed
    
    # Try to load a built-in icon if we don't have a custom one
    try:
        icon = app.style().standardIcon(app.style().StandardPixmap.SP_ComputerIcon)
    except:
        icon = QIcon() # Fallback to empty icon

    window = MainWindow()
    
    # Set up System Tray
    tray_icon = QSystemTrayIcon(icon, app)
    tray_icon.setToolTip("Game Translator Overlay")
    
    # Context Menu for Tray
    tray_menu = QMenu()
    
    action_show = tray_menu.addAction("Mở Cài Đặt (Khung Chính)")
    action_show.triggered.connect(window.showNormal)
    
    action_toggle_trans = tray_menu.addAction("Bật/Tắt Dịch")
    action_toggle_trans.triggered.connect(window.toggle_translation_loop)
    
    tray_menu.addSeparator()
    
    action_quit = tray_menu.addAction("Thoát (Exit)")
    # Using window.quit_app will ensure settings are saved before exiting
    action_quit.triggered.connect(window.quit_app)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()
    
    # Left click tray icon to show window
    def on_tray_icon_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            window.showNormal()
    tray_icon.activated.connect(on_tray_icon_activated)

    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
