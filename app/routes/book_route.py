from flask import Blueprint, request, render_template, redirect, url_for, flash
# from app.models.book_model import BookModel, TagModel, BookTagModel

# 建立 Blueprint 以方便註冊與管理路由
books_bp = Blueprint('books', __name__)

@books_bp.route('/')
@books_bp.route('/books')
def index():
    """
    顯示所有筆記列表。
    可透過 URL 參數 `?search=keyword` 來進行搜尋。
    """
    pass

@books_bp.route('/books/create', methods=['GET'])
def create_form():
    """
    顯示新增筆記的空白表單頁面 (create.html)。
    """
    pass

@books_bp.route('/books/create', methods=['POST'])
def create_book():
    """
    接收表單提交的新增筆記資料，寫入資料庫後重導向回首頁。
    若驗證失敗則重新渲染表單並顯示錯誤訊息。
    """
    pass

@books_bp.route('/books/<int:book_id>')
def view_book(book_id):
    """
    顯示單筆筆記的詳細資訊 (view.html)。
    若找不到對應的 ID，則回傳 404 錯誤。
    """
    pass

@books_bp.route('/books/<int:book_id>/edit', methods=['GET'])
def edit_form(book_id):
    """
    顯示編輯筆記的表單頁面 (edit.html)，並將現有資料預填入表單。
    若找不到對應的 ID，則回傳 404 錯誤。
    """
    pass

@books_bp.route('/books/<int:book_id>/edit', methods=['POST'])
def update_book(book_id):
    """
    接收編輯表單提交的變更資料，更新資料庫後重導向至筆記詳情頁。
    若驗證失敗則重新渲染表單並顯示錯誤訊息。
    """
    pass

@books_bp.route('/books/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    刪除指定的筆記紀錄，完成後重導向回首頁。
    （使用 POST 避免直接透過 URL 觸發刪除的資安風險）
    """
    pass
