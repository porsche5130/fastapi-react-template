# 重啟服務指令

## 環境資訊
- 後端 PORT: **10181**
- 前端 PORT: **10180**
- 資料庫: PostgreSQL (localhost:5432/pa64_dev)

## 1. 重啟後端服務

### 方式 A: uvicorn 直接執行
```bash
cd W:\P-PA6.4\Develop\backend

# 停止現有服務 (Ctrl+C)
# 然後重新啟動
uvicorn app.main:app --reload --host 0.0.0.0 --port 10181
```

### 方式 B: Python 直接執行
```bash
cd W:\P-PA6.4\Develop\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 10181
```

### 方式 C: 背景執行（Windows）
```bash
cd W:\P-PA6.4\Develop\backend
start /b python -m uvicorn app.main:app --host 0.0.0.0 --port 10181
```

## 2. 測試後端 API

### 健康檢查
```bash
curl http://localhost:10181/api/health
```

### 測試新 API 端點
```bash
# 使用者角色（需要 token）
curl http://localhost:10181/api/user_roles

# 角色權限（需要 token）
curl http://localhost:10181/api/role_rights

# 使用者日誌（需要 token）
curl http://localhost:10181/api/user_logs

# 系統首頁（需要 token）
curl http://localhost:10181/api/home/stats
```

### 查看 API 文件
開啟瀏覽器：
```
http://localhost:10181/docs
```

## 3. 前端開發測試

### 安裝依賴（如需要）
```bash
cd W:\P-PA6.4\Develop\frontend
npm install
```

### 啟動開發伺服器
```bash
cd W:\P-PA6.4\Develop\frontend
npm run dev
```

前端會在 http://localhost:10180 啟動

### 重新建置生產版本
```bash
cd W:\P-PA6.4\Develop\frontend
npm run build
```

## 4. 驗證清單

### 後端驗證
- [ ] 後端服務在 port 10181 啟動成功
- [ ] `/api/health` 返回健康狀態
- [ ] `/docs` 可以開啟 API 文件
- [ ] 新 API 端點在文件中可見：
  - [ ] `/api/user_roles`
  - [ ] `/api/role_rights`
  - [ ] `/api/user_logs`
  - [ ] `/api/home/*`

### 前端驗證
- [ ] 前端在 port 10180 啟動成功
- [ ] 可以正常登入
- [ ] 首頁 (/home) 正常顯示
- [ ] 系統選單正常載入
- [ ] 可以存取使用者角色管理頁面
- [ ] 可以存取角色權限管理頁面
- [ ] 可以存取使用者日誌頁面

### 資料庫驗證
```sql
-- 確認新表已建立
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('user_logs', 'user_roles', 'role_rights');

-- 確認資料已遷移
SELECT
  (SELECT COUNT(*) FROM user_roles) as user_roles_count,
  (SELECT COUNT(*) FROM role_rights) as role_rights_count,
  (SELECT COUNT(*) FROM user_logs) as user_logs_count;

-- 確認 dashboard 已改為 home
SELECT id, func_code, module_code, func_cname
FROM system_functions
WHERE func_code = 'dashboard';
```

## 5. 常見問題

### Q: 後端啟動失敗
**A**: 檢查 port 10181 是否被佔用
```bash
# Windows
netstat -ano | findstr :10181

# 如果有程式佔用，可以終止該程式
taskkill /PID <PID> /F
```

### Q: 前端連不到後端
**A**: 確認 CORS 設定
- 後端的 ALLOWED_ORIGINS 應包含 http://localhost:10180
- 前端的 API base URL 應指向 http://localhost:10181

### Q: 資料庫連線錯誤
**A**: 檢查 .env 檔案中的 DATABASE_URL
```
DATABASE_URL=postgresql://dev:dev123@localhost:5432/pa64_dev
```

## 6. 日誌位置

### 後端日誌
- 執行 uvicorn 的終端機視窗

### 前端日誌
- 瀏覽器開發者工具 Console
- npm run dev 的終端機視窗

---

**更新日期**: 2026-01-21
