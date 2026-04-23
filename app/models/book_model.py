import sqlite3
import os

# 根據架構文件，資料庫檔案放在 instance/ 目錄下
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'database.db')

def get_db_connection():
    """建立並回傳與 SQLite 資料庫的連線"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 讓回傳的資料可以用字典的方式存取
    conn.execute("PRAGMA foreign_keys = 1")  # 啟用外鍵約束，支援 CASCADE DELETE
    return conn

class BookModel:
    @staticmethod
    def create(title, review, rating):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, review, rating) VALUES (?, ?, ?)",
            (title, review, rating)
        )
        conn.commit()
        book_id = cursor.lastrowid
        conn.close()
        return book_id

    @staticmethod
    def get_all(search_query=None):
        conn = get_db_connection()
        if search_query:
            query = "SELECT * FROM books WHERE title LIKE ? OR review LIKE ? ORDER BY created_at DESC"
            search_term = f"%{search_query}%"
            books = conn.execute(query, (search_term, search_term)).fetchall()
        else:
            books = conn.execute("SELECT * FROM books ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(book) for book in books]

    @staticmethod
    def get_by_id(book_id):
        conn = get_db_connection()
        book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
        conn.close()
        return dict(book) if book else None

    @staticmethod
    def update(book_id, title, review, rating):
        conn = get_db_connection()
        conn.execute(
            "UPDATE books SET title = ?, review = ?, rating = ? WHERE id = ?",
            (title, review, rating, book_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(book_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        conn.close()

class TagModel:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        tags = conn.execute("SELECT * FROM tags ORDER BY name ASC").fetchall()
        conn.close()
        return [dict(tag) for tag in tags]

    @staticmethod
    def create(name):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO tags (name) VALUES (?)", (name,))
            conn.commit()
            tag_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            # 標籤名稱已存在時，直接回傳其 ID
            tag = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
            tag_id = tag['id']
        conn.close()
        return tag_id

class BookTagModel:
    @staticmethod
    def add_tag_to_book(book_id, tag_id):
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO book_tags (book_id, tag_id) VALUES (?, ?)",
                (book_id, tag_id)
            )
            conn.commit()
        except sqlite3.Error:
            pass  # 如果關聯已存在，忽略錯誤
        finally:
            conn.close()

    @staticmethod
    def get_tags_by_book_id(book_id):
        conn = get_db_connection()
        query = '''
            SELECT t.id, t.name 
            FROM tags t
            JOIN book_tags bt ON t.id = bt.tag_id
            WHERE bt.book_id = ?
        '''
        tags = conn.execute(query, (book_id,)).fetchall()
        conn.close()
        return [dict(tag) for tag in tags]

    @staticmethod
    def remove_all_tags_from_book(book_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM book_tags WHERE book_id = ?", (book_id,))
        conn.commit()
        conn.close()
