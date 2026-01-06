from database.database import get_connection

class Book:
    def __init__(self, book_id, title, isbn, author_id, category, total, available):
        self.book_id = book_id
        self.title = title
        self.isbn = isbn
        self.author_id = author_id
        self.category = category
        self.total = total
        self.available = available

    @staticmethod
    def add_book(title, isbn, author_id, category, copies):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""INSERT INTO books (title, isbn, author_id, category, copies_total, copies_available)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (title, isbn, author_id, category, copies, copies))
        conn.commit()
        cur.close()
        conn.close()
