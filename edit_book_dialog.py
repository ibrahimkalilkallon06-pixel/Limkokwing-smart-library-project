from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database.database import get_connection

class EditBookDialog(QDialog):
    def __init__(self, book_id, parent=None):
        super().__init__(parent)
        self.book_id = book_id
        self.setWindowTitle("Edit Book")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        self.title_input = QLineEdit()
        layout.addWidget(QLabel("Title"))
        layout.addWidget(self.title_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)
        self.setLayout(layout)

        self.load_book()

    def load_book(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT title FROM books WHERE book_id=%s", (self.book_id,))
        row = cur.fetchone()
        if row:
            self.title_input.setText(row[0])
        cur.close(); conn.close()

    def save(self):
        title = self.title_input.text()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE books SET title=%s WHERE book_id=%s", (title, self.book_id))
        conn.commit()
        cur.close(); conn.close()
        QMessageBox.information(self, "Success", "Book updated!")
        self.close()
