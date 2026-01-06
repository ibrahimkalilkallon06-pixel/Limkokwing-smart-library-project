# gui/login_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QComboBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from database.database import get_connection
from gui.main_window import MainWindow


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Limkokwing University Smart Library")
        self.setGeometry(300, 100, 500, 600)
        self.setFixedSize(500, 600)
        self.setStyleSheet("background-color: #121212;")
        self.init_ui()

    def init_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        # ---------------- LOGO ----------------
        logo_label = QLabel()
        pixmap = QPixmap("assets/limkokwing logo.jpg")
        pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # ---------------- TITLE ----------------
        title = QLabel("Limkokwing University Sierra Leone\nSmart Library")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # ---------------- ROLE ----------------
        layout.addWidget(QLabel("Select Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Member", "Librarian"])
        self.role_combo.setStyleSheet(self.input_style())
        layout.addWidget(self.role_combo)

        # ---------------- USERNAME ----------------
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setStyleSheet(self.input_style())
        layout.addWidget(self.username_input)

        # ---------------- FULL NAME (MEMBERS) ----------------
        layout.addWidget(QLabel("Full Name (Members Only):"))
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Full name for members")
        self.fullname_input.setStyleSheet(self.input_style())
        layout.addWidget(self.fullname_input)

        # ---------------- PASSWORD ----------------
        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.input_style())
        layout.addWidget(self.password_input)

        # ---------------- BUTTONS ----------------
        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.login_btn.setStyleSheet(self.button_style("#0044cc"))
        self.create_btn = QPushButton("Create Account")
        self.create_btn.setStyleSheet(self.button_style("#00aa44"))
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.create_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # ---------------- ACTIONS ----------------
        self.login_btn.clicked.connect(self.login)
        self.create_btn.clicked.connect(self.create_account)

    # ---------------- STYLES ----------------
    def input_style(self):
        return "background-color: #222222; color: #ffffff; padding: 8px; border-radius: 5px;"

    def button_style(self, color):
        return f"""
            background-color: {color};
            color: #ffffff;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
        """

    # ---------------- LOGIN ----------------
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_combo.currentText().lower()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Enter both username and password")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, role FROM users WHERE username=%s AND password=%s AND role=%s",
                    (username, password, role))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            QMessageBox.warning(self, "Error", "Invalid credentials!")
            return

        user_obj = {"user_id": user[0], "username": user[1], "role": user[2]}
        self.open_main_window(user_obj)

    # ---------------- CREATE ACCOUNT ----------------
    def create_account(self):
        username = self.username_input.text().strip()
        fullname = self.fullname_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_combo.currentText().lower()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required!")
            return
        if role == "member" and not fullname:
            QMessageBox.warning(self, "Error", "Members must provide full name!")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE username=%s", (username,))
        if cur.fetchone():
            QMessageBox.warning(self, "Error", "Username already exists!")
            cur.close()
            conn.close()
            return

        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s) RETURNING user_id",
                    (username, password, role))
        user_id = cur.fetchone()[0]

        if role == "member":
            cur.execute("INSERT INTO members (user_id, full_name) VALUES (%s, %s)", (user_id, fullname))

        conn.commit()
        cur.close()
        conn.close()

        QMessageBox.information(self, "Success", "Account created successfully!")
        self.open_main_window({"user_id": user_id, "username": username, "role": role})

    # ---------------- OPEN MAIN WINDOW ----------------
    def open_main_window(self, user_obj):
        from gui.main_window import MainWindow
        self.main_window = MainWindow(user_obj)
        self.main_window.show()
        self.close()
