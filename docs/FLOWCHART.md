# 流程圖：讀書筆記本系統

本文件涵蓋使用者的操作流程圖（User Flow）與系統處理資料的序列圖（Sequence Diagram），並附帶各功能與路由的清單對照表。

## 1. 使用者流程圖（User Flow）

以下圖表展示使用者進入系統後的各種操作路徑，包含瀏覽列表、搜尋、新增筆記、編輯與刪除等行為。

```mermaid
flowchart LR
    A([使用者開啟系統]) --> B[首頁 - 筆記列表]
    
    B --> C{選擇操作}
    
    C -->|關鍵字搜尋或點擊標籤| D[刷新清單：顯示搜尋或過濾結果]
    D --> B
    
    C -->|點擊「新增筆記」| E[進入新增表單頁面]
    E --> F{填寫筆記資料}
    F -->|填寫完畢送出| B
    F -->|點擊取消| B
    
    C -->|點擊單筆紀錄| G[進入筆記詳細資訊頁面]
    
    G --> H{選擇操作}
    H -->|點擊「編輯」| I[進入編輯表單頁面]
    I -->|修改並儲存| G
    
    H -->|點擊「刪除」| J[系統確認視窗]
    J -->|確認刪除| B
    J -->|取消| G
    
    H -->|回首頁| B
```

## 2. 系統序列圖（Sequence Diagram）

以下序列圖描述使用者執行**「新增筆記紀錄」**時，從瀏覽器填寫表單到資料寫入 SQLite，最終重新導向顯示成功畫面的完整技術流程。

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Route
    participant Model as Database Model
    participant DB as SQLite

    User->>Browser: 點擊「新增筆記」並填寫表單 (書名/心得/評分)
    User->>Browser: 點擊「送出」按鈕
    Browser->>Flask: 發出 POST /books/create 請求
    
    Flask->>Flask: 檢查接收欄位是否齊全
    
    alt 欄位驗證失敗
        Flask-->>Browser: 返回錯誤提示，要求重新填寫
    else 驗證成功
        Flask->>Model: 呼叫新增邏輯 (create_book)
        Model->>DB: 執行 SQL (INSERT INTO books ...)
        DB-->>Model: 寫入資料庫完成
        Model-->>Flask: 操作成功
        Flask-->>Browser: 發送 302 Redirect，重導向至列表頁
        Browser->>Flask: 自動發出 GET / (請求首頁)
        Flask-->>Browser: 回傳更新後的 HTML
        Browser-->>User: 畫面更新，清單上顯示新填寫的筆記
    end
```

## 3. 功能清單對照表

本清單列出了每個操作行為所對應的 URL 路徑與 HTTP Request Method：

| 功能描述 | HTTP 方法 | URL 路徑 | 對應動作與頁面 |
| --- | --- | --- | --- |
| 檢視所有筆記列表 | `GET` | `/` 或 `/books` | 顯示首頁清單 `index.html`（可處理 `?search=` 參數） |
| 最新單筆詳細內容 | `GET` | `/books/<id>` | 取得該筆筆記並渲染至 `view.html` |
| 取得新增紀錄表單 | `GET` | `/books/create` | 顯示填寫用空白表單頁面 `create.html` |
| 提交新增筆記資料 | `POST` | `/books/create` | 接收表單內容、存入資料庫、重導向至清單 |
| 取得編輯紀錄表單 | `GET` | `/books/<id>/edit`| 將現有紀錄帶入編輯表單頁面 `edit.html` |
| 儲存編輯變更資料 | `POST` | `/books/<id>/edit`| 將修改後的值更新至資料庫（純表單通常使用 POST） |
| 刪除指定筆記 | `POST` | `/books/<id>/delete`| 在資料庫移除該筆資料並重導向回清單 |
