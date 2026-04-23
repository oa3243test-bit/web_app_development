from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.book_model import BookModel, TagModel, BookTagModel

# 建立 Blueprint 以方便註冊與管理路由
books_bp = Blueprint('books', __name__)

@books_bp.route('/')
@books_bp.route('/books')
def index():
    """
    顯示所有筆記列表。
    可透過 URL 參數 `?search=keyword` 來進行搜尋。
    """
    search_query = request.args.get('search', '').strip()
    try:
        books = BookModel.get_all(search_query)
        return render_template('index.html', books=books, search_query=search_query)
    except Exception as e:
        flash(f"載入筆記列表時發生錯誤：{str(e)}", "danger")
        return render_template('index.html', books=[], search_query=search_query)

@books_bp.route('/books/create', methods=['GET'])
def create_form():
    """
    顯示新增筆記的空白表單頁面 (create.html)。
    """
    return render_template('create.html')

@books_bp.route('/books/create', methods=['POST'])
def create_book():
    """
    接收表單提交的新增筆記資料，寫入資料庫後重導向回首頁。
    若驗證失敗則重新渲染表單並顯示錯誤訊息。
    """
    title = request.form.get('title', '').strip()
    review = request.form.get('review', '').strip()
    rating = request.form.get('rating', '').strip()

    # 驗證必填欄位
    if not title or not review or not rating:
        flash("請填寫所有必填欄位（書名、心得、評分）。", "danger")
        return render_template('create.html', title=title, review=review, rating=rating)

    # 驗證評分格式
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError("評分必須在 1 到 5 之間")
    except ValueError:
        flash("評分必須是 1 到 5 的整數。", "danger")
        return render_template('create.html', title=title, review=review, rating=rating)

    # 新增至資料庫
    try:
        BookModel.create(title, review, rating)
        flash("成功新增筆記！", "success")
        return redirect(url_for('books.index'))
    except Exception as e:
        flash(f"新增筆記時發生錯誤：{str(e)}", "danger")
        return render_template('create.html', title=title, review=review, rating=rating)

@books_bp.route('/books/<int:book_id>')
def view_book(book_id):
    """
    顯示單筆筆記的詳細資訊 (view.html)。
    若找不到對應的 ID，則回傳 404 錯誤。
    """
    try:
        book = BookModel.get_by_id(book_id)
        if not book:
            flash("找不到該筆記！", "danger")
            return redirect(url_for('books.index'))
        return render_template('view.html', book=book)
    except Exception as e:
        flash(f"載入筆記時發生錯誤：{str(e)}", "danger")
        return redirect(url_for('books.index'))

@books_bp.route('/books/<int:book_id>/edit', methods=['GET'])
def edit_form(book_id):
    """
    顯示編輯筆記的表單頁面 (edit.html)，並將現有資料預填入表單。
    若找不到對應的 ID，則回傳 404 錯誤。
    """
    try:
        book = BookModel.get_by_id(book_id)
        if not book:
            flash("找不到該筆記！", "danger")
            return redirect(url_for('books.index'))
        return render_template('edit.html', book=book)
    except Exception as e:
        flash(f"載入編輯頁面時發生錯誤：{str(e)}", "danger")
        return redirect(url_for('books.index'))

@books_bp.route('/books/<int:book_id>/edit', methods=['POST'])
def update_book(book_id):
    """
    接收編輯表單提交的變更資料，更新資料庫後重導向至筆記詳情頁。
    若驗證失敗則重新渲染表單並顯示錯誤訊息。
    """
    # 先確認該筆記存在
    try:
        book = BookModel.get_by_id(book_id)
        if not book:
            flash("找不到該筆記！", "danger")
            return redirect(url_for('books.index'))
    except Exception as e:
        flash(f"驗證筆記時發生錯誤：{str(e)}", "danger")
        return redirect(url_for('books.index'))

    title = request.form.get('title', '').strip()
    review = request.form.get('review', '').strip()
    rating = request.form.get('rating', '').strip()

    # 建立一個暫存的資料物件以在驗證失敗時將使用者填寫的值帶回前端表單
    temp_book = {'id': book_id, 'title': title, 'review': review, 'rating': rating}

    if not title or not review or not rating:
        flash("請填寫所有必填欄位（書名、心得、評分）。", "danger")
        return render_template('edit.html', book=temp_book)

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError("評分必須在 1 到 5 之間")
    except ValueError:
        flash("評分必須是 1 到 5 的整數。", "danger")
        return render_template('edit.html', book=temp_book)

    try:
        BookModel.update(book_id, title, review, rating)
        flash("成功更新筆記！", "success")
        return redirect(url_for('books.view_book', book_id=book_id))
    except Exception as e:
        flash(f"更新筆記時發生錯誤：{str(e)}", "danger")
        return render_template('edit.html', book=temp_book)

@books_bp.route('/books/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    刪除指定的筆記紀錄，完成後重導向回首頁。
    （使用 POST 避免直接透過 URL 觸發刪除的資安風險）
    """
    try:
        BookModel.delete(book_id)
        flash("成功刪除筆記！", "success")
    except Exception as e:
        flash(f"刪除筆記時發生錯誤：{str(e)}", "danger")
    
    return redirect(url_for('books.index'))
