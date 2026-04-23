# 路由設計文件 (API Design)

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| --- | --- | --- | --- | --- |
| 筆記列表 | GET | `/` 或 `/books` | `index.html` | 顯示所有筆記，並支援 `?search=` 關鍵字搜尋 |
| 新增筆記頁面 | GET | `/books/create` | `create.html` | 顯示新增筆記的空白表單 |
| 建立筆記 | POST | `/books/create` | — | 接收表單，存入 DB 後重導向至首頁 |
| 筆記詳情 | GET | `/books/<int:id>` | `view.html` | 顯示單一筆記詳細內容與心得 |
| 編輯筆記頁面 | GET | `/books/<int:id>/edit` | `edit.html` | 顯示包含既有資料的編輯表單 |
| 更新筆記 | POST | `/books/<int:id>/edit` | — | 接收表單，更新 DB 後重導向至該筆記詳情頁 |
| 刪除筆記 | POST | `/books/<int:id>/delete` | — | 從 DB 刪除該筆記後重導向至首頁 |

## 2. 每個路由的詳細說明

### 筆記列表 (`GET /` 或 `GET /books`)
- **輸入**: URL 參數 `search`（可選）。
- **處理邏輯**: 
  - 呼叫 `BookModel.get_all(search_query)` 獲取資料庫中的筆記列表。
- **輸出**: 渲染 `index.html`，傳遞 `books` 列表。
- **錯誤處理**: 若資料庫連線或讀取失敗，返回 500 錯誤。

### 新增筆記頁面 (`GET /books/create`)
- **輸入**: 無。
- **處理邏輯**: 僅作為顯示表單的入口。
- **輸出**: 渲染 `create.html`。

### 建立筆記 (`POST /books/create`)
- **輸入**: 表單欄位 `title` (必填), `review` (必填), `rating` (1-5 的整數)。
- **處理邏輯**:
  - 驗證表單是否齊全且評分是否在合理範圍。
  - 呼叫 `BookModel.create(title, review, rating)`。
- **輸出**: 重導向 (302 Redirect) 至 `/` (或 `/books`)。
- **錯誤處理**: 若驗證失敗，渲染 `create.html` 並傳遞錯誤訊息要求重新填寫。

### 筆記詳情 (`GET /books/<int:id>`)
- **輸入**: URL 路徑參數 `id`。
- **處理邏輯**: 呼叫 `BookModel.get_by_id(id)` 取得單筆資料。
- **輸出**: 渲染 `view.html`，傳遞 `book` 資料。
- **錯誤處理**: 若找不到該 `id` 的資料，返回 404 錯誤頁面。

### 編輯筆記頁面 (`GET /books/<int:id>/edit`)
- **輸入**: URL 路徑參數 `id`。
- **處理邏輯**: 呼叫 `BookModel.get_by_id(id)` 取得單筆資料以預先填入表單。
- **輸出**: 渲染 `edit.html`，傳遞 `book` 資料。
- **錯誤處理**: 若找不到該 `id` 的資料，返回 404 錯誤。

### 更新筆記 (`POST /books/<int:id>/edit`)
- **輸入**: URL 路徑參數 `id`，表單欄位 `title`, `review`, `rating`。
- **處理邏輯**: 
  - 驗證表單輸入。
  - 呼叫 `BookModel.update(id, title, review, rating)` 更新資料。
- **輸出**: 重導向至該筆記詳情頁 `/books/<id>`。
- **錯誤處理**: 若驗證失敗，帶上錯誤訊息重新渲染 `edit.html`。

### 刪除筆記 (`POST /books/<int:id>/delete`)
- **輸入**: URL 路徑參數 `id`。
- **處理邏輯**: 呼叫 `BookModel.delete(id)` 刪除對應的資料。
- **輸出**: 重導向至 `/` (或 `/books`)。
- **錯誤處理**: 若找不到該 `id` 的資料，則可能返回 404，或者安全地忽略。

## 3. Jinja2 模板清單

所有的 HTML 頁面都會放置於 `app/templates/` 目錄下：

- `base.html`: 共用的基礎佈局 (Base Template)，包含全域的 Header (導覽列)、Footer 及預先引用的 CSS/JS。
- `index.html`: 首頁清單頁，繼承自 `base.html`。包含搜尋列與筆記列表的卡片或表格。
- `create.html`: 新增筆記頁面，繼承自 `base.html`。包含輸入書籍資訊的表單。
- `edit.html`: 編輯筆記頁面，繼承自 `base.html`。表單結構同 `create.html`，但需綁定舊有資料。
- `view.html`: 筆記詳細資訊頁面，繼承自 `base.html`。顯示完整心得內容，並包含「編輯」與「刪除」的按鈕。

## 4. 路由骨架程式碼

路由骨架實作於 `app/routes/book_route.py` 中。
