from database.database import get_connection

class BookClub:
    def __init__(self, club_id, name, description):
        self.club_id = club_id
        self.name = name
        self.description = description

    @staticmethod
    def join_club(member_id, club_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM club_members WHERE member_id=%s AND club_id=%s", (member_id, club_id))
        if not cur.fetchone():
            cur.execute("INSERT INTO club_members (member_id, club_id) VALUES (%s, %s)", (member_id, club_id))
            conn.commit()
        cur.close(); conn.close()
