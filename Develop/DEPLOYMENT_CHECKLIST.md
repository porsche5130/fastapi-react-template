# 部署檢查清單：sysfunction → system_functions

## 📋 部署前檢查

### 環境準備

- [ ] 已備份資料庫（完整備份）
- [ ] 已備份應用程式碼
- [ ] 已通知所有開發人員和使用者
- [ ] 已規劃維護時間窗口
- [ ] 已準備回滾計畫

### 程式碼準備

- [ ] 所有變更已提交到版本控制
- [ ] 已在開發環境測試所有功能
- [ ] 後端程式碼已審查
- [ ] 前端程式碼已審查
- [ ] 文件已更新

## 🚀 部署步驟

### 第一階段：資料庫遷移

#### 1. 連接資料庫

```bash
# 使用 psql 連接
psql -U your_username -d your_database_name

# 或使用 Python 腳本
cd Develop/backend
python migrations/run_migration.py
```

#### 2. 執行遷移腳本

使用 Python 腳本（推薦）：
```bash
python migrations/run_migration.py
```

或手動執行 SQL：
```sql
\i migrations/01_create_system_functions_table.sql
\i migrations/02_migrate_data_to_system_functions.sql
```

#### 3. 驗證遷移結果

```sql
-- 檢查兩個表是否都存在
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('sysfunction', 'system_functions');

-- 檢查資料數量
SELECT 'sysfunction' as table_name, COUNT(*) FROM sysfunction
UNION ALL
SELECT 'system_functions' as table_name, COUNT(*) FROM system_functions;

-- 檢查 module_code 欄位
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'system_functions'
AND column_name = 'module_code';

-- 檢查 system_functions 記錄
SELECT id, func_code, module_code, func_cname
FROM system_functions
WHERE func_code = 'system_functions';
```

- [ ] 新表 system_functions 已建立
- [ ] 資料已完整遷移
- [ ] module_code 欄位存在
- [ ] system_functions 記錄的 func_code 已更新為 'system_functions'
- [ ] 資料數量一致

### 第二階段：部署後端

#### 1. 停止後端服務

```bash
# 停止 FastAPI 服務
# 視您的部署方式而定，例如：
sudo systemctl stop fastapi
# 或
pm2 stop fastapi
```

#### 2. 更新後端程式碼

```bash
cd Develop/backend
git pull origin main  # 或您的分支名稱
```

#### 3. 確認檔案存在

- [ ] app/models/system_functions.py 存在
- [ ] app/schemas/system_functions.py 存在
- [ ] app/routes/system_functions.py 存在
- [ ] app/main.py 已更新（包含新路由）
- [ ] app/routes/system.py 已更新（支援新舊表）

#### 4. 重啟後端服務

```bash
# 重啟 FastAPI 服務
sudo systemctl start fastapi
# 或
pm2 start fastapi
```

#### 5. 驗證後端服務

```bash
# 檢查服務狀態
sudo systemctl status fastapi
# 或
pm2 status

# 測試 API 端點
curl http://localhost:8000/api/health
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/system_functions/
```

- [ ] 後端服務啟動成功
- [ ] API 健康檢查通過
- [ ] 新路由 /api/system_functions 可存取
- [ ] 舊路由 /api/sysfunction 仍可存取（向下兼容）

### 第三階段：部署前端

#### 1. 更新前端程式碼

```bash
cd Develop/frontend
git pull origin main
```

#### 2. 安裝依賴（如有新增）

```bash
npm install
```

#### 3. 確認檔案存在

- [ ] src/types/systemFunctions.ts 存在
- [ ] src/services/systemFunctionsService.ts 存在
- [ ] src/pages/SystemFunctionsPage.tsx 存在
- [ ] src/App.tsx 已更新（包含新路由）
- [ ] src/types/index.ts 已更新（支援 module_code）

#### 4. 建置前端

```bash
npm run build
```

- [ ] 建置成功，無錯誤
- [ ] 無 TypeScript 錯誤

#### 5. 部署前端檔案

```bash
# 視您的部署方式而定
# 例如：複製 dist 到 nginx 目錄
sudo cp -r dist/* /var/www/html/
```

#### 6. 重啟 Web 伺服器

```bash
sudo systemctl restart nginx
```

## ✅ 部署後測試

### 功能測試

#### 1. 基本存取測試

- [ ] 登入系統
- [ ] 儀表板正常顯示
- [ ] 選單正常載入

#### 2. 新系統功能測試（/system_functions）

- [ ] 可以存取 /system_functions 頁面
- [ ] 可以看到系統功能列表
- [ ] 可以建立新功能
- [ ] 可以編輯功能
- [ ] 可以刪除功能
- [ ] 可以查看功能詳情
- [ ] 搜尋功能正常
- [ ] 過濾功能正常
- [ ] 分頁功能正常

#### 3. 舊系統功能測試（/sysfunction）

- [ ] 可以存取 /sysfunction 頁面（向下兼容）
- [ ] 基本功能正常

#### 4. 選單功能測試

- [ ] Sidebar 選單正常顯示
- [ ] 選單項目可以點擊
- [ ] 路由導航正常
- [ ] 多層選單展開/收合正常

#### 5. API 測試

使用 Postman 或 curl 測試：

```bash
# 取得系統功能列表（新 API）
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/system_functions/

# 取得樹狀結構
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/system_functions/tree

# 取得選單（會自動使用新表）
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/system/functions
```

- [ ] 所有 API 端點回應正常
- [ ] 資料格式正確
- [ ] module_code 欄位存在

#### 6. 權限測試

- [ ] 權限檢查使用 'system_functions' func_code
- [ ] 無權限使用者無法存取
- [ ] 有權限使用者可以正常操作

#### 7. 日誌測試

- [ ] 操作有正確記錄到 userlogs
- [ ] func_code 記錄為 'system_functions'
- [ ] 日誌內容完整

### 效能測試

- [ ] 頁面載入時間正常（< 3 秒）
- [ ] API 回應時間正常（< 1 秒）
- [ ] 資料庫查詢效能正常

### 相容性測試

- [ ] Chrome 瀏覽器正常
- [ ] Firefox 瀏覽器正常
- [ ] Edge 瀏覽器正常
- [ ] 行動裝置瀏覽器正常

## 🔄 監控期

### 第一週監控重點

- [ ] 每日檢查系統日誌
- [ ] 監控錯誤率
- [ ] 收集使用者反饋
- [ ] 檢查效能指標
- [ ] 確認無重大問題

### 問題追蹤

如發現問題：

1. **記錄問題**
   - 問題描述
   - 重現步驟
   - 錯誤訊息
   - 影響範圍

2. **評估嚴重性**
   - 嚴重：立即回滾
   - 中等：規劃修復
   - 輕微：記錄追蹤

3. **處理方案**
   - 修復 bug
   - 或執行回滾計畫

## 🔙 回滾計畫

如需回滾：

### 1. 前端回滾

```bash
cd Develop/frontend
git checkout PREVIOUS_COMMIT
npm run build
sudo cp -r dist/* /var/www/html/
sudo systemctl restart nginx
```

### 2. 後端回滾

```bash
cd Develop/backend
git checkout PREVIOUS_COMMIT
sudo systemctl restart fastapi
```

### 3. 資料同步（如需要）

```sql
-- 如果新表有新增資料，需要同步回舊表
INSERT INTO sysfunction (
    func_code, upper_func_id, func_cname, func_ename,
    func_type, func_order, func_icon, func_module_name,
    module_item, description, is_mana, is_active,
    edit_by, created_at, updated_at
)
SELECT
    func_code, upper_func_id, func_cname, func_ename,
    func_type, func_order, func_icon, module_code,
    module_item, description, is_mana, is_active,
    edit_by, created_at, updated_at
FROM system_functions
WHERE id NOT IN (SELECT id FROM sysfunction)
ON CONFLICT (id) DO UPDATE SET
    func_code = EXCLUDED.func_code,
    func_module_name = EXCLUDED.func_module_name,
    updated_at = CURRENT_TIMESTAMP;
```

- [ ] 前端已回滾
- [ ] 後端已回滾
- [ ] 資料已同步（如需要）
- [ ] 系統功能正常

## 🧹 清理階段（一週後）

確認系統穩定運作至少一週後：

### 1. 移除舊路由

#### 後端 (app/main.py)

```python
# 移除或註解掉
# app.include_router(sysfunction.router, prefix="/api/sysfunction", tags=["系統功能（舊）"])
```

#### 前端 (src/App.tsx)

```typescript
// 移除或註解掉
// <Route path="sysfunction" element={<SysFunctionsPage />} />
```

### 2. 刪除舊檔案

```bash
# 後端
rm app/models/sysfunction.py
rm app/schemas/sysfunction.py
rm app/routes/sysfunction.py

# 前端
rm src/services/sysfunctionService.ts
rm src/pages/SysFunctionsPage.tsx
```

### 3. 執行資料庫清理

```bash
psql -U your_username -d your_database_name -f migrations/03_cleanup_old_sysfunction.sql
```

- [ ] 舊路由已移除
- [ ] 舊檔案已刪除
- [ ] 舊表已刪除
- [ ] 備份表存在

### 4. 最終驗證

- [ ] 系統功能正常
- [ ] 無錯誤日誌
- [ ] 使用者反饋良好

## 📝 清理備份（一個月後）

確認系統穩定運作至少一個月後：

```sql
-- 刪除備份表
DROP TABLE IF EXISTS sysfunction_backup_final;
DROP TABLE IF EXISTS sysfunction_backup_20260121;
```

- [ ] 備份表已刪除
- [ ] 系統運作正常

## 📊 部署總結

### 完成日期

- 資料庫遷移：____年__月__日
- 後端部署：____年__月__日
- 前端部署：____年__月__日
- 舊系統清理：____年__月__日
- 備份清理：____年__月__日

### 問題記錄

| 日期 | 問題描述 | 嚴重性 | 處理方式 | 處理人 | 狀態 |
|------|---------|--------|---------|--------|------|
|      |         |        |         |        |      |

### 經驗總結

- 成功經驗：
- 改進建議：
- 注意事項：

## 📞 聯絡資訊

- 技術負責人：________
- 緊急聯絡電話：________
- Email：________

---

**重要提醒**：
1. 執行每個步驟前請仔細閱讀
2. 遇到問題立即停止並尋求協助
3. 所有操作都要有備份
4. 詳細記錄所有變更和問題
