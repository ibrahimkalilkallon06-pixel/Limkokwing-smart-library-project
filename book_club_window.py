# gui/book_club_window.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from database.database import get_connection

class BookClubWindow(QDialog):
    def __init__(self, role, user_id=None, parent=None):
        super().__init__(parent)
        self.role = role
        self.user_id = user_id

        self.setWindowTitle("Book Clubs")
        self.setFixedSize(650, 520)
        self.setStyleSheet("background-color: #111111; color: white;")

        layout = QVBoxLayout()

        title = QLabel("Book Clubs")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Clubs table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget { background-color: #1a1a1a; color: white; gridline-color: #333333; }
            QHeaderView::section { background-color: #222222; color: white; padding: 5px; }
        """)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()

        self.join_btn = QPushButton("Join Club")
        self.join_btn.setStyleSheet("background-color: black; color: white; padding: 10px;")
        self.leave_btn = QPushButton("Leave Club")
        self.leave_btn.setStyleSheet("background-color: black; color: white; padding: 10px;")
        btn_layout.addWidget(self.join_btn)
        btn_layout.addWidget(self.leave_btn)

        if self.role == "librarian":
            self.view_members_btn = QPushButton("View Members")
            self.view_members_btn.setStyleSheet("background-color: black; color: white; padding: 10px;")
            btn_layout.addWidget(self.view_members_btn)

            self.create_btn = QPushButton("Create Club")
            self.create_btn.setStyleSheet("background-color: black; color: white; padding: 10px;")
            btn_layout.addWidget(self.create_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Connect buttons
        self.join_btn.clicked.connect(self.join_club)
        self.leave_btn.clicked.connect(self.leave_club)
        if self.role == "librarian":
            self.create_btn.clicked.connect(self.create_club_dialog)
            self.view_members_btn.clicked.connect(self.view_members_dialog)

        # Load clubs from database
        self.load_clubs()

    # ----------------------------
    # Load all clubs
    # ----------------------------
    def load_clubs(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT club_id, name, description FROM book_clubs ORDER BY name")
            rows = cur.fetchall()

            self.table.setRowCount(len(rows))
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["ID", "Name", "Description"])

            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.table.setItem(r, c, QTableWidgetItem(str(val)))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load clubs:\n{e}")
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass

    # ----------------------------
    # Join club
    # ----------------------------
    def join_club(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a club first!")
            return
        club_id = int(self.table.item(row, 0).text())

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM club_members WHERE club_id=%s AND member_id=%s", (club_id, self.user_id))
            if cur.fetchone():
                QMessageBox.information(self, "Info", "Already joined!")
            else:
                cur.execute("INSERT INTO club_members (club_id, member_id) VALUES (%s, %s)", (club_id, self.user_id))
                conn.commit()
                QMessageBox.information(self, "Success", "Joined club!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to join club:\n{e}")
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass

    # ----------------------------
    # Leave club
    # ----------------------------
    def leave_club(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a club first!")
            return
        club_id = int(self.table.item(row, 0).text())

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM club_members WHERE club_id=%s AND member_id=%s", (club_id, self.user_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Left club!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to leave club:\n{e}")
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass

    # ----------------------------
    # Create club (librarian)
    # ----------------------------
    def create_club_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Create Club")
        dlg.setFixedSize(400, 250)
        dlg.setStyleSheet("background-color: #111111; color: white;")
        layout = QVBoxLayout(dlg)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Club Name")
        desc_input = QTextEdit()
        desc_input.setPlaceholderText("Description")
        create_btn = QPushButton("Create")
        create_btn.setStyleSheet("background-color: black; color: white; padding: 10px;")

        layout.addWidget(name_input)
        layout.addWidget(desc_input)
        layout.addWidget(create_btn)

        def create():
            name = name_input.text().strip()
            desc = desc_input.toPlainText().strip()
            if not name:
                QMessageBox.warning(dlg, "Error", "Name is required!")
                return
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO book_clubs (name, description) VALUES (%s, %s)", (name, desc))
                conn.commit()
                QMessageBox.information(dlg, "Success", "Club created!")
                dlg.close()
                self.load_clubs()
            except Exception as e:
                QMessageBox.critical(dlg, "Error", f"Failed to create club:\n{e}")
            finally:
                try:
                    cur.close()
                    conn.close()
                except:
                    pass

        create_btn.clicked.connect(create)
        dlg.exec_()

    # ----------------------------
    # View members (librarian)
    # ----------------------------
    def view_members_dialog(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a club!")
            return
        club_id = int(self.table.item(row, 0).text())

        dlg = QDialog(self)
        dlg.setWindowTitle("Club Members")
        dlg.setFixedSize(500, 400)
        dlg.setStyleSheet("background-color: #111111; color: white;")
        layout = QVBoxLayout(dlg)

        label = QLabel("Members in this Club")
        label.setFont(QFont("Arial", 14, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)

        table = QTableWidget()
        table.setStyleSheet("""
            QTableWidget { background-color: #1a1a1a; color: white; }
            QHeaderView::section { background-color: #222222; color: white; padding: 5px; }
        """)

        layout.addWidget(label)
        layout.addWidget(table)

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT m.member_id, m.full_name, u.username
                FROM club_members cm
                JOIN members m ON m.member_id = cm.member_id
                JOIN users u ON u.user_id = m.user_id
                WHERE cm.club_id = %s
            """, (club_id,))
            rows = cur.fetchall()

            table.setRowCount(len(rows))
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["ID", "Full Name", "Username"])
            for r, row_data in enumerate(rows):
                for c, val in enumerate(row_data):
                    table.setItem(r, c, QTableWidgetItem(str(val)))
            table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(dlg, "Error", f"Failed to load members:\n{e}")
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass

        dlg.exec_()
