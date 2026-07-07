# main.py
import sys
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QObject, QEvent
import config
from sound_manager import SoundManager
from popup_manager import PopupManager
from unlock_dialog import UnlockDialog

class KeyPressFilter(QObject):
    """Global event filter to catch the Ctrl+Shift+U shortcut from anywhere in the application."""
    
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            # Check for Ctrl + Shift + U
            if (event.modifiers() & Qt.KeyboardModifier.ControlModifier and 
                event.modifiers() & Qt.KeyboardModifier.ShiftModifier and 
                event.key() == Qt.Key.Key_U):
                self.main_app.show_unlock_dialog()
                return True
        return super().eventFilter(obj, event)

class PrankApp:
    """Main application orchestrating sound, popups, and user input."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # Prevent the application from exiting if the user closes all current popups.
        # It must keep running until cleanly unlocked.
        self.app.setQuitOnLastWindowClosed(False)
        
        self.sound_manager = SoundManager(config.AUDIO_PATH)
        self.popup_manager = PopupManager()
        
        # Install a global event filter to catch the unlock shortcut
        self.key_filter = KeyPressFilter(self)
        self.app.installEventFilter(self.key_filter)
        
        self.unlock_dialog = None
        
    def run(self):
        """Starts the prank."""
        self.sound_manager.start_playing()
        self.popup_manager.start_spawning()
        sys.exit(self.app.exec())
        
    def show_unlock_dialog(self):
        """Shows the unlock dialog if it's not already visible."""
        if self.unlock_dialog is not None and self.unlock_dialog.isVisible():
            self.unlock_dialog.raise_()
            self.unlock_dialog.activateWindow()
            return
            
        self.unlock_dialog = UnlockDialog(config.PASSPHRASE)
        if self.unlock_dialog.exec():
            # If exec() returns True (accepted), the correct passphrase was entered
            self.stop_prank()
            
    def stop_prank(self):
        """Stops the prank and exits cleanly."""
        self.popup_manager.stop_all()
        self.sound_manager.stop_playing()
        self.app.quit()

if __name__ == "__main__":
    # Hide the terminal window on Windows
    if os.name == 'nt':
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        
    app = PrankApp()
    app.run()
