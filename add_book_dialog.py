from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from models.book import Book

class AddBookDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Book")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()

        self.title = QLineEdit(); self.isbn = QLineEdit(); self.author = QLineEdit(); self.category = QLineEdit(); self.copies = QLineEdit()
        layout.addWidget(QLabel("Title")); layout.addWidget(self.title)
        layout.addWidget(QLabel("ISBN")); layout.addWidget(self.isbn)
        layout.addWidget(QLabel("Author ID")); layout.addWidget(self.author)
        layout.addWidget(QLabel("Category")); layout.addWidget(self.category)
        layout.addWidget(QLabel("Copies")); layout.addWidget(self.copies)

        btn = QPushButton("Add Book"); btn.clicked.connect(self.add_book)
        layout.addWidget(btn); self.setLayout(layout)

    def add_book(self):
        try:
            Book.add_book(self.title.text(), self.isbn.text(), self.author.text(),
                          self.category.text(), int(self.copies.text()))
            QMessageBox.information(self, "Success", "Book added!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
