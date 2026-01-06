from database.database import get_connection

class Member:
    def __init__(self, member_id, user_id, full_name):
        self.member_id = member_id
        self.user_id = user_id
        self.full_name = full_name

    def borrow_book(self, book_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT copies_available FROM books WHERE book_id=%s", (book_id,))
        available = cur.fetchone()[0]
        if available <= 0:
            cur.close(); conn.close()
            raise Exception("No copies available")
        cur.execute("INSERT INTO loans (book_id, member_id, due_date, status) VALUES (%s, %s, CURRENT_DATE + INTERVAL '14 days', 'borrowed')",
                    (book_id, self.member_id))
        cur.execute("UPDATE books SET copies_available = copies_available - 1 WHERE book_id=%s", (book_id,))
        conn.commit(); cur.close(); conn.close()
