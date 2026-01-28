# PA6.4 系統部署指南

## 部署日期
2026-01-21

## 概述

本次部署採用「先建後拆」策略，進行資料表命名標準化：
- `userlogs` → `user_logs`
- `user_role` → `user_roles`
- `role_right` → `role_rights`
- `dashboard` 模組改名為 `home` 作為系統首頁

## 變更摘要

### 後端變更

#### 新增模型檔案
- `app/models/user_logs.py` - 使用者日誌模型（新版）
- `app/models/user_roles.py` - 使用者角色模型（新版）
- `app/models/role_rights.py` - 角色權限模型（新版）

#### 新增 Schema 檔案
- `app/schemas/user_logs.py`
- `app/schemas/user_roles.py`
- `app/schemas/role_rights.py`

#### 新增 Route 檔案
- `app/routes/user_logs.py`
- `app/routes/user_roles.py`
- `app/routes/role_rights.py`
- `app/routes/home.py` - 系統首頁 API

#### 更新檔案
- `app/main.py` - 註冊新路由（新舊並存）

#### 資料庫遷移腳本
- `migrations/04_create_new_tables.sql` - 建立新資料表
- `migrations/05_migrate_data_to_new_tables.sql` - 遷移資料
- `migrations/06_cleanup_old_tables.sql` - 清理舊資料表（確認穩定後執行）
- `run_table_migration.py` - Python 遷移執行腳本

### 前端變更

#### 新增服務檔案
- `src/services/userLogsService.ts`
- `src/services/userRolesService.ts`
- `src/services/roleRightsService.ts`
- `src/services/homeService.ts`

#### 新增頁面
- `src/pages/HomePage.tsx` - 系統首頁

#### 更新檔案
- `src/App.tsx` - 新增 home 路由
- `src/locales/zh-TW/translation.json` - 新增首頁翻譯

### API 端點變更

#### 新增端點（新舊並存）
```
POST   /api/user_roles      （新）  vs  /api/user_role     （舊）
GET    /api/user_roles      （新）  vs  /api/user_role     （舊）
PUT    /api/user_roles/{id} （新）  vs  /api/user_role/{id}（舊）
DELETE /api/user_roles/{id} （新）  vs  /api/user_role/{id}（舊）

POST   /api/role_rights      （新）  vs  /api/role_right     （舊）
GET    /api/role_rights      （新）  vs  /api/role_right     （舊）
PUT    /api/role_rights/{id} （新）  vs  /api/role_right/{id}（舊）
DELETE /api/role_rights/{id} （新）  vs  /api/role_right/{id}（舊）

POST   /api/user_logs      （新）  vs  /api/userlogs     （舊）
GET    /api/user_logs      （新）  vs  /api/userlogs     （舊）
GET    /api/user_logs/{id} （新）  vs  /api/userlogs/{id}（舊）

GET    /api/home/stats           - 首頁統計資訊
GET    /api/home/activities      - 最近活動記錄
GET    /api/home/quick-links     - 快速連結
```

## 部署步驟

### 1. 備份資料庫

```bash
# 備份整個資料庫
pg_dump -U postgres -d pa64 > backup_$(date +%Y%m%d_%H%M%S).sql

# 或使用內建的 Python 腳本備份
cd W:\P-PA6.4\Develop\backend
python backup_system_functions.py
```

### 2. 停止服務

```bash
# 停止後端服務
# （依您的部署方式而定）
sudo systemctl stop fastapi
# 或
pm2 stop pa64-backend
```

### 3. 更新程式碼

```bash
cd W:\P-PA6.4
git pull origin master
# 或直接複製新版程式碼
```

### 4. 執行資料庫遷移

```bash
cd W:\P-PA6.4\Develop\backend

# 執行遷移腳本
python run_table_migration.py

# 或手動執行 SQL
psql -U postgres -d pa64 -f migrations/04_create_new_tables.sql
psql -U postgres -d pa64 -f migrations/05_migrate_data_to_new_tables.sql
```

### 5. 更新 system_functions 資料

```bash
cd W:\P-PA6.4\Develop\backend

# 還原 system_functions 資料（包含 dashboard → home 的更新）
python restore_system_functions.py
```

### 6. 安裝新依賴（如有）

```bash
# 後端
cd W:\P-PA6.4\Develop\backend
pip install -r requirements.txt

# 前端
cd W:\P-PA6.4\Develop\frontend
npm install
```

### 7. 重新建置前端

```bash
cd W:\P-PA6.4\Develop\frontend
npm run build
```

### 8. 啟動服務

```bash
# 啟動後端服務
sudo systemctl start fastapi
# 或
pm2 start pa64-backend

# 確認服務狀態
sudo systemctl status fastapi
# 或
pm2 status
```

### 9. 驗證部署

#### 檢查後端 API

```bash
# 檢查健康狀態
curl http://localhost:8000/api/health

# 檢查 API 文件
# 瀏覽器開啟: http://localhost:8000/docs

# 測試新端點
curl http://localhost:8000/api/user_roles
curl http://localhost:8000/api/role_rights
curl http://localhost:8000/api/user_logs
curl http://localhost:8000/api/home/stats
```

#### 檢查前端

1. 瀏覽器開啟系統首頁
2. 登入系統
3. 確認首頁 (home) 正常顯示
4. 測試以下功能：
   - 使用者角色管理
   - 角色權限管理
   - 使用者日誌查詢

#### 檢查資料庫

```sql
-- 確認新資料表已建立
SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  AND tablename IN ('user_logs', 'user_roles', 'role_rights');

-- 確認資料已遷移
SELECT
  (SELECT COUNT(*) FROM user_role) as old_user_role,
  (SELECT COUNT(*) FROM user_roles) as new_user_roles,
  (SELECT COUNT(*) FROM role_right) as old_role_right,
  (SELECT COUNT(*) FROM role_rights) as new_role_rights,
  (SELECT COUNT(*) FROM userlogs) as old_userlogs,
  (SELECT COUNT(*) FROM user_logs) as new_user_logs;

-- 確認 dashboard 已改為 home
SELECT id, func_code, module_code, func_cname
FROM system_functions
WHERE func_code = 'dashboard';
```

## 測試清單

### 基本功能測試

- [ ] 使用者登入
- [ ] 首頁顯示正常
- [ ] 系統選單正常顯示
- [ ] 使用者登出

### 新功能測試

- [ ] 首頁統計資訊顯示
- [ ] 使用者角色管理（新版 API）
  - [ ] 新增角色
  - [ ] 查詢角色
  - [ ] 修改角色
  - [ ] 刪除角色
- [ ] 角色權限管理（新版 API）
  - [ ] 設定權限
  - [ ] 查詢權限
  - [ ] 修改權限
  - [ ] 刪除權限
- [ ] 使用者日誌（新版 API）
  - [ ] 查詢日誌
  - [ ] 篩選日誌

### 向下相容性測試

- [ ] 舊版使用者角色 API 仍可使用
- [ ] 舊版角色權限 API 仍可使用
- [ ] 舊版使用者日誌 API 仍可使用
- [ ] 舊版 dashboard 路由仍可存取

## 常見問題

### Q1: 遷移後資料筆數不一致？

**A:** 檢查是否有外鍵約束問題：

```sql
-- 檢查 role_rights 遷移問題
SELECT COUNT(*) FROM role_right rr
LEFT JOIN sysfunction sf ON rr.sysfunction_id = sf.id
WHERE sf.id IS NULL;

-- 如果有資料，表示有舊的 sysfunction_id 在 system_functions 中找不到對應
```

### Q2: 新版 API 返回 404？

**A:** 確認後端服務已重啟，並檢查 main.py 是否正確匯入新路由：

```python
from app.routes import user_roles, role_rights, user_logs, home
```

### Q3: 前端頁面空白？

**A:** 檢查瀏覽器控制台錯誤訊息，確認前端已重新建置：

```bash
cd W:\P-PA6.4\Develop\frontend
npm run build
```

### Q4: 首頁無法載入？

**A:** 確認 App.tsx 中的首頁路由設定：

```typescript
<Route index element={<Navigate to="/home" replace />} />
<Route path="home" element={<HomePage />} />
```

## 回滾計畫

如果部署後發現重大問題，可執行以下回滾步驟：

### 1. 回滾程式碼

```bash
cd W:\P-PA6.4
git reset --hard HEAD~1
# 或還原到特定版本
git reset --hard <commit-hash>
```

### 2. 回滾資料庫（如已執行清理）

```bash
# 從備份還原
psql -U postgres -d pa64 < backup_YYYYMMDD_HHMMSS.sql
```

### 3. 重啟服務

```bash
sudo systemctl restart fastapi
```

## 後續工作

### 一週後

1. 確認系統穩定運作
2. 檢查日誌是否有異常
3. 收集使用者反饋

### 穩定後（建議至少一週）

執行清理腳本，移除舊資料表：

```bash
cd W:\P-PA6.4\Develop\backend
psql -U postgres -d pa64 -f migrations/06_cleanup_old_tables.sql
```

### 一個月後

刪除最終備份表：

```sql
DROP TABLE IF EXISTS user_role_backup_final;
DROP TABLE IF EXISTS role_right_backup_final;
DROP TABLE IF EXISTS userlogs_backup_final;
```

## 支援聯絡

如有問題，請聯絡：
- 技術負責人：________
- Email：________
- 電話：________

---

**部署完成日期**: __________
**部署人員**: __________
**驗證人員**: __________
