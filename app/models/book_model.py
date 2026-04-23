import sqlite3
import os

# 根據架構文件，資料庫檔案放在 instance/ 目錄下
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'database.db')

def get_db_connection():
    """
    建立並回傳與 SQLite 資料庫的連線。
    如果連線失敗會拋出例外。
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 讓回傳的資料可以用字典的方式存取
        conn.execute("PRAGMA foreign_keys = 1")  # 啟用外鍵約束，支援 CASCADE DELETE
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise

class BookModel:
    @staticmethod
    def create(title, review, rating):
        """
        新增一筆讀書筆記記錄到資料庫。
        :param title: 書名
        :param review: 閱讀心得
        :param rating: 評分 (1-5)
        :return: 新增的資料 id
        """
        try:
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
        except sqlite3.Error as e:
            print(f"Error creating book: {e}")
            raise

    @staticmethod
    def get_all(search_query=None):
        """
        取得所有的讀書筆記記錄，可選擇性地透過搜尋字串過濾。
        :param search_query: 搜尋關鍵字 (對應書名或心得)
        :return: 包含多筆字典的 list
        """
        try:
            conn = get_db_connection()
            if search_query:
                query = "SELECT * FROM books WHERE title LIKE ? OR review LIKE ? ORDER BY created_at DESC"
                search_term = f"%{search_query}%"
                books = conn.execute(query, (search_term, search_term)).fetchall()
            else:
                books = conn.execute("SELECT * FROM books ORDER BY created_at DESC").fetchall()
            conn.close()
            return [dict(book) for book in books]
        except sqlite3.Error as e:
            print(f"Error fetching books: {e}")
            return []

    @staticmethod
    def get_by_id(book_id):
        """
        根據 id 取得單筆讀書筆記記錄。
        :param book_id: 筆記 id
        :return: 單筆資料的字典，若找不到則回傳 None
        """
        try:
            conn = get_db_connection()
            book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
            conn.close()
            return dict(book) if book else None
        except sqlite3.Error as e:
            print(f"Error fetching book by id: {e}")
            return None

    @staticmethod
    def update(book_id, title, review, rating):
        """
        更新特定 id 的讀書筆記記錄。
        :param book_id: 筆記 id
        :param title: 新的書名
        :param review: 新的閱讀心得
        :param rating: 新的評分 (1-5)
        """
        try:
            conn = get_db_connection()
            conn.execute(
                "UPDATE books SET title = ?, review = ?, rating = ? WHERE id = ?",
                (title, review, rating, book_id)
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error updating book: {e}")
            raise

    @staticmethod
    def delete(book_id):
        """
        刪除特定 id 的讀書筆記記錄。
        :param book_id: 筆記 id
        """
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error deleting book: {e}")
            raise

class TagModel:
    @staticmethod
    def get_all():
        """
        取得所有的標籤。
        :return: 標籤清單的 list
        """
        try:
            conn = get_db_connection()
            tags = conn.execute("SELECT * FROM tags ORDER BY name ASC").fetchall()
            conn.close()
            return [dict(tag) for tag in tags]
        except sqlite3.Error as e:
            print(f"Error fetching tags: {e}")
            return []

    @staticmethod
    def create(name):
        """
        建立新的標籤，若已存在則直接回傳該標籤的 id。
        :param name: 標籤名稱
        :return: 標籤的 id
        """
        try:
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
        except sqlite3.Error as e:
            print(f"Error creating tag: {e}")
            raise

class BookTagModel:
    @staticmethod
    def add_tag_to_book(book_id, tag_id):
        """
        新增筆記與標籤的關聯。
        :param book_id: 筆記 id
        :param tag_id: 標籤 id
        """
        try:
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
        except sqlite3.Error as e:
            print(f"Error adding tag to book: {e}")
            raise

    @staticmethod
    def get_tags_by_book_id(book_id):
        """
        取得特定筆記關聯的所有標籤。
        :param book_id: 筆記 id
        :return: 標籤字典清單的 list
        """
        try:
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
        except sqlite3.Error as e:
            print(f"Error fetching tags by book id: {e}")
            return []

    @staticmethod
    def remove_all_tags_from_book(book_id):
        """
        移除特定筆記的所有標籤關聯。
        :param book_id: 筆記 id
        """
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM book_tags WHERE book_id = ?", (book_id,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error removing tags from book: {e}")
            raise
