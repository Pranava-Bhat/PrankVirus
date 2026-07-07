# unlock_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

class UnlockDialog(QDialog):
    """Hidden dialog that prompts for the passphrase to stop the prank."""
    
    def __init__(self, expected_passphrase, parent=None):
        super().__init__(parent)
        self.expected_passphrase = expected_passphrase
        
        self.setWindowTitle("Unlock")
        
        # Ensure the dialog appears on top of everything so the user can easily interact with it
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)
        
        layout = QVBoxLayout()
        
        self.label = QLabel("Enter passphrase to stop:")
        layout.addWidget(self.label)
        
        self.input_field = QLineEdit()
        self.input_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_field.returnPressed.connect(self.check_passphrase)
        layout.addWidget(self.input_field)
        
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.check_passphrase)
        layout.addWidget(self.submit_btn)
        
        self.setLayout(layout)
        
    def check_passphrase(self):
        """Verifies the entered passphrase."""
        if self.input_field.text() == self.expected_passphrase:
            self.accept()
        else:
            self.input_field.clear()
            self.label.setText("Incorrect passphrase. Try again:")
            self.label.setStyleSheet("color: red;")
