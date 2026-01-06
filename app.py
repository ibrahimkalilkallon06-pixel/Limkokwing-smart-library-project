# run.py
import sys
from PyQt5.QtWidgets import QApplication
from gui.login_window import LoginWindow

def main():
    app = QApplication(sys.argv)

    # ---- DARK THEME (BLACK UI) ----
    dark_stylesheet = """
        QWidget {
            background-color: #000000;
            color: #FFFFFF;
            font-size: 14px;
        }

        QLineEdit, QComboBox, QTextEdit {
            background-color: #111111;
            border: 1px solid #444444;
            padding: 6px;
            color: white;
        }

        QPushButton {
            background-color: #c8102e;  /* Limkokwing red */
            border: none;
            padding: 8px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: blue;
        }

        QPushButton:pressed {
            background-color: #990000;
        }

        QLabel {
            color: blue;
        }

        QDialog {
            background-color: black;
            color: white;
        }

        QMessageBox {
            background-color: black;
            color: white;
        }

        QInputDialog {
            background-color: black;
            color: white;
        }
    """
    app.setStyleSheet(dark_stylesheet)
    # --------------------------------

    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
