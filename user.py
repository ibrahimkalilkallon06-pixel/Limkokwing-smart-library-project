from database.database import get_connection

class User:
    def __init__(self, user_id, username, role):
        self.user_id = user_id
        self.username = username
        self.role = role

    @classmethod
    def authenticate(cls, username, password):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, role FROM users WHERE username=%s AND password=%s",
                    (username, password))
        row = cur.fetchone()
        cur.close(); conn.close()
        if row:
            return cls(row[0], username, row[1])
        return None
