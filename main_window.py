# gui/main_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from database.database import get_connection
from gui.add_book_dialog import AddBookDialog
from gui.edit_book_dialog import EditBookDialog


class MainWindow(QMainWindow):
    def __init__(self, user_name, role, user_id):
        super().__init__()
        self.user_name = user_name
        self.role = role  # 'librarian' or 'member'
        self.user_id = user_id
        self.setWindowTitle(f"Limkokwing University Smart Library - {self.user_name} ({self.role.capitalize()})")
        self.setGeometry(150, 100, 1200, 720)

        # central layout
        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout()
        central.setLayout(self.layout)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()
        header = QLabel("Limkokwing University of Creative Technology - Smart Library")
        header.setStyleSheet("font-size:18pt; font-weight:bold; color:#FFC300;")
        header.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(header)

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("background:#B30000; color:blue; padding:8px 14px; border-radius:6px;")
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)
        self.layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Determine member_id (for member users)
        self.member_id = None
        if self.role == "member":
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute("SELECT member_id FROM members WHERE user_id=%s", (self.user_id,))
                r = cur.fetchone()
                if r:
                    self.member_id = r[0]
                cur.close(); conn.close()
            except Exception:
                self.member_id = None

        # Role-specific tabs
        if self.role == "librarian":
            self.create_manage_books_tab()
            self.create_manage_members_tab()
            self.create_manage_book_clubs_tab()
        else:
            self.create_borrow_tab()
            self.create_return_tab()
            self.create_book_club_tab()

    # ----------------- Logout -----------------
    def logout(self):
        from gui.login_window import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()

    # ----------------- Manage Books (Librarian) -----------------
    def create_manage_books_tab(self):
        self.books_tab = QWidget()
        l = QVBoxLayout(); l.setContentsMargins(8, 8, 8, 8)
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(7)
        self.books_table.setHorizontalHeaderLabels(["ID", "Title", "ISBN", "Author ID", "Category", "Total", "Available"])
        self.books_table.setAlternatingRowColors(True)
        l.addWidget(self.books_table)

        btn_h = QHBoxLayout()
        add_btn = QPushButton("Add Book"); add_btn.clicked.connect(self.add_book)
        edit_btn = QPushButton("Edit Selected"); edit_btn.clicked.connect(self.edit_book)
        del_btn = QPushButton("Delete Selected"); del_btn.clicked.connect(self.delete_book)
        btn_h.addWidget(add_btn); btn_h.addWidget(edit_btn); btn_h.addWidget(del_btn)
        l.addLayout(btn_h)

        self.books_tab.setLayout(l)
        self.tabs.addTab(self.books_tab, "Manage Books")
        self.load_books()

    def load_books(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT book_id, title, isbn, author_id, category, copies_total, copies_available FROM books ORDER BY title")
            rows = cur.fetchall()
            self.books_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.books_table.setItem(r, c, QTableWidgetItem(str(val if val is not None else "")))
            self.books_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load books:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def add_book(self):
        dlg = AddBookDialog(self)
        if dlg.exec_():
            self.load_books()

    def edit_book(self):
        sel = self.books_table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Error", "Select a book to edit")
            return
        book_id = int(self.books_table.item(sel, 0).text())
        dlg = EditBookDialog(book_id, self)
        if dlg.exec_():
            self.load_books()

    def delete_book(self):
        sel = self.books_table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Error", "Select a book to delete")
            return
        book_id = int(self.books_table.item(sel, 0).text())
        confirm = QMessageBox.question(self, "Confirm Delete", f"Delete book ID {book_id}?")
        if confirm != QMessageBox.Yes:
            return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
            conn.commit()
            QMessageBox.information(self, "Success", "Book deleted.")
            self.load_books()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete book:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    # ----------------- Manage Members (Librarian) -----------------
    def create_manage_members_tab(self):
        self.members_tab = QWidget()
        l = QVBoxLayout(); l.setContentsMargins(8,8,8,8)

        # All members table
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(4)
        self.members_table.setHorizontalHeaderLabels(["Member ID", "Username", "Full Name", "Join Date"])
        l.addWidget(QLabel("All Members:"))
        l.addWidget(self.members_table)

        # Member loans overview
        self.member_loans_table = QTableWidget()
        self.member_loans_table.setColumnCount(6)
        self.member_loans_table.setHorizontalHeaderLabels(["Loan ID", "Member ID", "Member Name", "Book ID", "Title", "Status"])
        l.addWidget(QLabel("Member Loans:"))
        l.addWidget(self.member_loans_table)

        # Club selection for viewing members
        club_h = QHBoxLayout()
        club_h.addWidget(QLabel("View Members by Book Club:"))
        self.club_combobox = QComboBox()
        self.club_combobox.currentIndexChanged.connect(self.load_members_by_club)
        club_h.addWidget(self.club_combobox)
        l.addLayout(club_h)

        self.club_members_table = QTableWidget()
        self.club_members_table.setColumnCount(3)
        self.club_members_table.setHorizontalHeaderLabels(["Member ID", "Full Name", "Username"])
        l.addWidget(QLabel("Members in selected club:"))
        l.addWidget(self.club_members_table)

        # Buttons to view selected member details
        btn_h = QHBoxLayout()
        view_loans_btn = QPushButton("View Selected Member Loans"); view_loans_btn.clicked.connect(self.view_selected_member_loans)
        view_clubs_btn = QPushButton("View Selected Member Clubs"); view_clubs_btn.clicked.connect(self.view_selected_member_clubs)
        btn_h.addWidget(view_loans_btn); btn_h.addWidget(view_clubs_btn)
        l.addLayout(btn_h)

        self.members_tab.setLayout(l)
        self.tabs.addTab(self.members_tab, "Manage Members")

        # load data
        self.load_members()
        self.load_member_loans()
        self.load_book_club_combobox()

    def load_members(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT m.member_id, u.username, m.full_name, m.join_date
                FROM members m
                LEFT JOIN users u ON m.user_id = u.user_id
                ORDER BY m.member_id
            """)
            rows = cur.fetchall()
            self.members_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.members_table.setItem(r, c, QTableWidgetItem(str(val if val is not None else "")))
            self.members_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load members:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def load_member_loans(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT l.loan_id, l.member_id, COALESCE(m.full_name, u.username) AS member_name,
                       b.book_id, b.title, l.status
                FROM loans l
                JOIN books b ON l.book_id = b.book_id
                LEFT JOIN members m ON l.member_id = m.member_id
                LEFT JOIN users u ON m.user_id = u.user_id
                ORDER BY l.loan_date DESC
            """)
            rows = cur.fetchall()
            self.member_loans_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.member_loans_table.setItem(r, c, QTableWidgetItem(str(val if val is not None else "")))
            self.member_loans_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load member loans:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def load_book_club_combobox(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT club_id, name FROM book_clubs ORDER BY name")
            rows = cur.fetchall()
            self.club_combobox.clear()
            self.club_combobox.addItem("Select a club", -1)
            for cid, name in rows:
                self.club_combobox.addItem(name, cid)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load clubs:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def load_members_by_club(self):
        club_id = self.club_combobox.currentData()
        if club_id is None or club_id == -1:
            self.club_members_table.setRowCount(0)
            return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT m.member_id, m.full_name, u.username
                FROM club_members cm
                JOIN members m ON cm.member_id = m.member_id
                LEFT JOIN users u ON m.user_id = u.user_id
                WHERE cm.club_id = %s
                ORDER BY m.full_name
            """, (club_id,))
            rows = cur.fetchall()
            self.club_members_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.club_members_table.setItem(r, c, QTableWidgetItem(str(val if val is not None else "")))
            self.club_members_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load club members:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def view_selected_member_loans(self):
        sel = self.members_table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Error", "Select a member first.")
            return
        member_id = int(self.members_table.item(sel, 0).text())
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT l.loan_id, b.title, l.loan_date, l.due_date, l.return_date, l.status
                FROM loans l
                JOIN books b ON l.book_id = b.book_id
                WHERE l.member_id = %s
                ORDER BY l.loan_date DESC
            """, (member_id,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load loans:\n{e}")
            return

        # show dialog
        dlg = QDialog(self); dlg.setWindowTitle("Member Loans"); dlg.setFixedSize(700, 400)
        v = QVBoxLayout(dlg)
        tbl = QTableWidget(); tbl.setColumnCount(6)
        tbl.setHorizontalHeaderLabels(["Loan ID", "Title", "Loan Date", "Due Date", "Return Date", "Status"])
        tbl.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                tbl.setItem(r, c, QTableWidgetItem(str(val if val is not None else "")))
        tbl.resizeColumnsToContents()
        v.addWidget(tbl)
        dlg.exec_()

    def view_selected_member_clubs(self):
        sel = self.members_table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Error", "Select a member first.")
            return
        member_id = int(self.members_table.item(sel, 0).text())
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT bc.club_id, bc.name
                FROM club_members cm
                JOIN book_clubs bc ON cm.club_id = bc.club_id
                WHERE cm.member_id = %s
                ORDER BY bc.name
            """, (member_id,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load member clubs:\n{e}")
            return

        dlg = QDialog(self); dlg.setWindowTitle("Member's Book Clubs"); dlg.setFixedSize(400, 300)
        v = QVBoxLayout(dlg)
        tbl = QTableWidget(); tbl.setColumnCount(2); tbl.setHorizontalHeaderLabels(["Club ID", "Name"])
        tbl.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                tbl.setItem(r, c, QTableWidgetItem(str(val if val is not None else "")))
        tbl.resizeColumnsToContents()
        v.addWidget(tbl)
        dlg.exec_()

    # ----------------- Manage Book Clubs (Librarian) -----------------
    def create_manage_book_clubs_tab(self):
        self.clubs_tab = QWidget()
        l = QVBoxLayout(); l.setContentsMargins(8,8,8,8)

        self.clubs_table = QTableWidget()
        self.clubs_table.setColumnCount(3)
        self.clubs_table.setHorizontalHeaderLabels(["Club ID", "Name", "Description"])
        l.addWidget(QLabel("Book Clubs:"))
        l.addWidget(self.clubs_table)

        btn_h = QHBoxLayout()
        add_btn = QPushButton("Create Club"); add_btn.clicked.connect(self.add_club)
        del_btn = QPushButton("Delete Selected Club"); del_btn.clicked.connect(self.delete_club)
        assign_btn = QPushButton("Assign Member to Club"); assign_btn.clicked.connect(self.assign_member_to_club)
        remove_btn = QPushButton("Remove Member from Club"); remove_btn.clicked.connect(self.remove_member_from_club)
        btn_h.addWidget(add_btn); btn_h.addWidget(del_btn); btn_h.addWidget(assign_btn); btn_h.addWidget(remove_btn)
        l.addLayout(btn_h)

        self.clubs_tab.setLayout(l)
        self.tabs.addTab(self.clubs_tab, "Manage Book Clubs")
        self.load_book_clubs_table()

    def load_book_clubs_table(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT club_id, name, description FROM book_clubs ORDER BY name")
            rows = cur.fetchall()
            self.clubs_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.clubs_table.setItem(r, c, QTableWidgetItem(str(val if val is not None else "")))
            self.clubs_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load book clubs:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def add_club(self):
        name, ok = QInputDialog.getText(self, "Create Club", "Club name:")
        if not ok or not name.strip():
            return
        desc, ok2 = QInputDialog.getText(self, "Create Club", "Description (optional):")
        if not ok2:
            desc = ""
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO book_clubs (name, description) VALUES (%s, %s)", (name.strip(), desc.strip()))
            conn.commit()
            QMessageBox.information(self, "Success", "Book club created.")
            self.load_book_clubs_table()
            self.load_book_club_combobox()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create club:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def delete_club(self):
        sel = self.clubs_table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Error", "Select a club to delete")
            return
        club_id = int(self.clubs_table.item(sel, 0).text())
        confirm = QMessageBox.question(self, "Confirm", f"Delete club {club_id}?")
        if confirm != QMessageBox.Yes:
            return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM book_clubs WHERE club_id=%s", (club_id,))
            conn.commit()
            QMessageBox.information(self, "Success", "Club deleted.")
            self.load_book_clubs_table()
            self.load_book_club_combobox()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete club:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def assign_member_to_club(self):
        # ask for member id and club id (or use selected)
        try:
            member_id, ok1 = QInputDialog.getInt(self, "Assign Member", "Member ID:")
            if not ok1:
                return
            club_id, ok2 = QInputDialog.getInt(self, "Assign Member", "Club ID:")
            if not ok2:
                return
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT 1 FROM club_members WHERE club_id=%s AND member_id=%s", (club_id, member_id))
            if cur.fetchone():
                QMessageBox.information(self, "Info", "Member already in club.")
            else:
                cur.execute("INSERT INTO club_members (club_id, member_id) VALUES (%s, %s)", (club_id, member_id))
                conn.commit()
                QMessageBox.information(self, "Success", "Member assigned to club.")
            self.load_members_by_club()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to assign member:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def remove_member_from_club(self):
        try:
            member_id, ok1 = QInputDialog.getInt(self, "Remove Member", "Member ID:")
            if not ok1:
                return
            club_id, ok2 = QInputDialog.getInt(self, "Remove Member", "Club ID:")
            if not ok2:
                return
            conn = get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM club_members WHERE club_id=%s AND member_id=%s", (club_id, member_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Member removed from club.")
            self.load_members_by_club()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove member:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    # ----------------- Member Tabs -----------------
    def create_borrow_tab(self):
        self.borrow_tab = QWidget()
        l = QVBoxLayout(); l.setContentsMargins(8,8,8,8)
        self.available_books_table = QTableWidget()
        self.available_books_table.setColumnCount(6)
        self.available_books_table.setHorizontalHeaderLabels(["ID", "Title", "ISBN", "Category", "Total", "Available"])
        l.addWidget(QLabel("Available Books:"))
        l.addWidget(self.available_books_table)
        borrow_btn = QPushButton("Borrow Selected Book"); borrow_btn.clicked.connect(self.borrow_book)
        l.addWidget(borrow_btn)
        self.borrow_tab.setLayout(l)
        self.tabs.addTab(self.borrow_tab, "Borrow Books")
        self.load_available_books()

    def load_available_books(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT book_id, title, isbn, category, copies_total, copies_available FROM books ORDER BY title")
            rows = cur.fetchall()
            self.available_books_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.available_books_table.setItem(r, c, QTableWidgetItem(str(val if val is not None else "")))
            self.available_books_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load available books:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def borrow_book(self):
        if self.member_id is None:
            QMessageBox.warning(self, "Error", "Member record not found!")
            return
        sel = self.available_books_table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Error", "Select a book to borrow")
            return
        book_id = int(self.available_books_table.item(sel, 0).text())
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT copies_available FROM books WHERE book_id=%s", (book_id,))
            a = cur.fetchone()
            if not a or a[0] <= 0:
                QMessageBox.warning(self, "Error", "No copies available")
                cur.close(); conn.close(); return
            cur.execute("SELECT COUNT(*) FROM loans WHERE member_id=%s AND status='borrowed'", (self.member_id,))
            active = cur.fetchone()[0]
            if active >= 3:
                QMessageBox.warning(self, "Error", "You cannot borrow more than 3 books at a time")
                cur.close(); conn.close(); return
            # due_date required in schema: set 14 days
            cur.execute("INSERT INTO loans (book_id, member_id, due_date, status) VALUES (%s, %s, CURRENT_DATE + INTERVAL '14 days', 'borrowed')",
                        (book_id, self.member_id))
            cur.execute("UPDATE books SET copies_available = copies_available - 1 WHERE book_id=%s", (book_id,))
            conn.commit()
            QMessageBox.information(self, "Success", "Book borrowed successfully!")
            self.load_available_books()
            self.load_borrowed_books()
            self.load_member_loans()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to borrow book:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def create_return_tab(self):
        self.return_tab = QWidget()
        l = QVBoxLayout(); l.setContentsMargins(8,8,8,8)
        self.borrowed_table = QTableWidget()
        self.borrowed_table.setColumnCount(5)
        self.borrowed_table.setHorizontalHeaderLabels(["Loan ID", "Book ID", "Title", "Loan Date", "Due Date"])
        l.addWidget(QLabel("My Borrowed Books:"))
        l.addWidget(self.borrowed_table)
        return_btn = QPushButton("Return Selected Book"); return_btn.clicked.connect(self.return_book)
        l.addWidget(return_btn)
        self.return_tab.setLayout(l)
        self.tabs.addTab(self.return_tab, "Return Books")
        self.load_borrowed_books()

    def load_borrowed_books(self):
        if self.member_id is None:
            return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT l.loan_id, b.book_id, b.title, l.loan_date, l.due_date
                FROM loans l
                JOIN books b ON l.book_id = b.book_id
                WHERE l.member_id=%s AND l.status='borrowed'
            """, (self.member_id,))
            rows = cur.fetchall()
            self.borrowed_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.borrowed_table.setItem(r, c, QTableWidgetItem(str(val if val is not None else "")))
            self.borrowed_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load borrowed books:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def return_book(self):
        sel = self.borrowed_table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Error", "Select a book to return")
            return
        loan_id = int(self.borrowed_table.item(sel, 0).text())
        book_id = int(self.borrowed_table.item(sel, 1).text())
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("UPDATE loans SET status='returned', return_date=CURRENT_DATE WHERE loan_id=%s", (loan_id,))
            cur.execute("UPDATE books SET copies_available = copies_available + 1 WHERE book_id=%s", (book_id,))
            conn.commit()
            QMessageBox.information(self, "Success", "Book returned successfully!")
            self.load_available_books()
            self.load_borrowed_books()
            self.load_member_loans()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to return book:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    # ----------------- Book Clubs (Member view) -----------------
    def create_book_club_tab(self):
        self.club_tab = QWidget()
        l = QVBoxLayout(); l.setContentsMargins(8,8,8,8)
        self.club_table = QTableWidget()
        self.club_table.setColumnCount(3)
        self.club_table.setHorizontalHeaderLabels(["ID", "Name", "Description"])
        l.addWidget(QLabel("Available Book Clubs:"))
        l.addWidget(self.club_table)

        btn_h = QHBoxLayout()
        join_btn = QPushButton("Join Selected Club"); join_btn.clicked.connect(self.join_club)
        leave_btn = QPushButton("Leave Selected Club"); leave_btn.clicked.connect(self.leave_club)
        btn_h.addWidget(join_btn); btn_h.addWidget(leave_btn)
        l.addLayout(btn_h)

        self.club_tab.setLayout(l)
        self.tabs.addTab(self.club_tab, "Book Clubs")
        self.load_book_clubs()

    def load_book_clubs(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT club_id, name, description FROM book_clubs ORDER BY name")
            rows = cur.fetchall()
            self.club_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.club_table.setItem(r, c, QTableWidgetItem(str(val if val is not None else "")))
            self.club_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load clubs:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def join_club(self):
        if self.member_id is None:
            QMessageBox.warning(self, "Error", "Member record not found!")
            return
        sel = self.club_table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Error", "Select a club to join")
            return
        club_id = int(self.club_table.item(sel, 0).text())
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT 1 FROM club_members WHERE club_id=%s AND member_id=%s", (club_id, self.member_id))
            if cur.fetchone():
                QMessageBox.information(self, "Info", "Already joined this club")
            else:
                cur.execute("INSERT INTO club_members (club_id, member_id) VALUES (%s, %s)", (club_id, self.member_id))
                conn.commit()
                QMessageBox.information(self, "Success", "Joined club successfully!")
            self.load_book_clubs()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to join club:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass

    def leave_club(self):
        if self.member_id is None:
            QMessageBox.warning(self, "Error", "Member record not found!")
            return
        sel = self.club_table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Error", "Select a club to leave")
            return
        club_id = int(self.club_table.item(sel, 0).text())
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM club_members WHERE club_id=%s AND member_id=%s", (club_id, self.member_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Left club successfully!")
            self.load_book_clubs()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to leave club:\n{e}")
        finally:
            try: cur.close(); conn.close()
            except: pass
