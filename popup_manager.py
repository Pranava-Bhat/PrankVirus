# popup_manager.py
import random
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtGui import QPixmap, QTransform, QFont, QCursor
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
import config

class Popup(QWidget):
    """A single popup window displaying an image and a warning message."""
    
    def __init__(self, base_pixmap, message):
        super().__init__()
        
        # Frameless window, stays on top, tool window (so it doesn't clutter taskbar)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.Tool)
                            
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Allow the popup to be clicked/focused so global shortcuts can be caught
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Image label
        self.img_label = QLabel()
        
        if not base_pixmap.isNull():
            # Apply random scale and rotation to the base image
            scale = random.uniform(0.5, 1.2)
            angle = random.uniform(-30, 30)
            
            transform = QTransform().scale(scale, scale).rotate(angle)
            pixmap = base_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            
            self.img_label.setPixmap(pixmap)
            self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.img_label)
            
        # Warning message label
        self.msg_label = QLabel(message)
        self.msg_label.setStyleSheet(
            "color: white; background-color: red; "
            "padding: 10px; border: 2px solid darkred; border-radius: 5px;"
        )
        font = QFont("Arial", 16, QFont.Weight.Bold)
        self.msg_label.setFont(font)
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.msg_label)
        
        self.setLayout(layout)
        
        # Position the popup randomly on the primary screen
        self.adjustSize()
        screen_geometry = QApplication.primaryScreen().geometry()
        max_x = max(0, screen_geometry.width() - self.width())
        max_y = max(0, screen_geometry.height() - self.height())
        self.move(random.randint(0, max_x), random.randint(0, max_y))
        
        # Apply fade-in animation
        self.setWindowOpacity(0.0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.start()
        
    def mousePressEvent(self, event):
        """Allow dragging the popup manually just for fun or better interaction."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

class PopupManager:
    """Manages the continuous spawning of popup windows."""
    
    def __init__(self):
        self.popups = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.spawn_popup)
        
        # Load and scale base image once to prevent massive memory usage
        # from loading/transforming huge images repeatedly
        self.base_pixmap = QPixmap(config.IMAGE_PATH)
        if not self.base_pixmap.isNull():
            # Scale down to a reasonable max size (e.g., max 500x500)
            self.base_pixmap = self.base_pixmap.scaled(
                500, 500, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
    def start_spawning(self):
        """Starts the popup spawning cycle."""
        self.spawn_popup()
        
    def spawn_popup(self):
        """Creates a new popup and schedules the next one."""
        popup = Popup(self.base_pixmap, config.WARNING_MESSAGE)
        # Ensure memory is cleaned up if user manually closes a popup (e.g. Alt+F4)
        popup.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        popup.show()
        
        # Give the newly created popup focus so keyboard events (like our unlock shortcut)
        # can be intercepted by the application event filter without having to explicitly click.
        popup.activateWindow()
        popup.setFocus()
        
        self.popups.append(popup)
        
        # Schedule the next spawn
        next_interval = random.uniform(config.POPUP_INTERVAL_MIN, config.POPUP_INTERVAL_MAX) * 1000
        self.timer.start(int(next_interval))
        
    def stop_all(self):
        """Stops spawning and closes all active popups."""
        self.timer.stop()
        for popup in self.popups:
            try:
                popup.close()
            except RuntimeError:
                # If popup was already closed by the user, its C++ object is deleted
                pass
        self.popups.clear()
