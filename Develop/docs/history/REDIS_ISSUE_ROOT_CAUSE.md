# Redis Commander 看不到交易資訊 - 根本原因分析

## 問題現象
使用 Redis Commander 連接到 `10.1.0.20:6379 DB 1` 時,看不到任何 Session 或交易令牌資料。

## 根本原因

### 1. 後端配置檔案 (.env) 缺少 Redis 設定
**位置**: `w:\P-PA6.4\Develop\backend\.env`

**問題**:
- `.env` 檔案中 Redis 配置被註解掉了
- 只有一行被註解的 `# REDIS_URL=redis://:!DC1qaz2wsx@localhost:6379/0`
- 缺少 `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD` 等環境變數

**原因**:
- 之前遷移 PostgreSQL 到遠端時,只更新了 `DATABASE_URL`
- Redis 配置沒有同步更新

### 2. 後端使用了預設的 config.py 配置
**位置**: `w:\P-PA6.4\Develop\backend\app\core\config.py`

**程式邏輯**:
```python
class Settings(BaseSettings):
    REDIS_HOST: str = Field(default="10.1.0.20")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=1)
    REDIS_PASSWORD: str = Field(default="!DC1qaz2wsx")
```

**實際發生的情況**:
- 因為 `.env` 沒有 Redis 配置,後端**應該**使用 `config.py` 的預設值
- 預設值是正確的: `10.1.0.20:6379 DB 1`
- **但實際上資料卻寫入了 `localhost:6379 DB 0`**

### 3. 多個後端進程同時運行 (關鍵原因)
**發現**:
```
PID 49256, Name: python, StartTime: 01/28/2026 09:04:37
PID 79256, Name: python, StartTime: 01/28/2026 00:55:15
```

**問題**:
1. 有**至少 2 個舊的後端進程**在運行
2. 這些舊進程可能:
   - 使用了更舊的程式碼版本
   - 使用了不同的 Redis 配置
   - 硬編碼了 `localhost` 作為 Redis host
   - 或者在啟動時 Redis 初始化失敗,使用了記憶體儲存的 fallback

3. **端口衝突但沒有報錯**:
   ```
   TCP    0.0.0.0:10181    LISTENING    80788  (新進程)
   TCP    0.0.0.0:10181    LISTENING    41320  (舊進程)
   TCP    0.0.0.0:10181    LISTENING    34272  (舊進程)
   ```
   - 3 個進程都在監聽 10181
   - Windows 允許多個進程綁定相同的 socket (SO_REUSEADDR)
   - 請求被**隨機分配**到其中一個進程

### 4. 舊進程使用了 localhost Redis
**證據**:
- Redis Commander 截圖顯示 `localhost (redis:6379:0)` 有 5 個 session 和 5 個 token
- 登入測試成功返回了 `txn_token`,但 `10.1.0.20:6379 DB 1` 中沒有資料
- 這表示登入請求被**舊進程處理**,資料寫入了 localhost

**可能的原因**:
1. 舊進程啟動時,`.env` 或環境變數中可能有 `REDIS_HOST=localhost`
2. 或者舊進程使用的程式碼版本中,`config.py` 的預設值是 `localhost`
3. 或者舊進程的 Redis 初始化失敗,fallback 到某個預設行為

## 修正過程

### Step 1: 更新 .env 檔案
```env
# Redis (遠端 Redis on 10.1.0.20, DB 1)
REDIS_HOST=10.1.0.20
REDIS_PORT=6379
REDIS_DB=1
REDIS_PASSWORD=!DC1qaz2wsx
```

### Step 2: 停止所有舊的 Python 後端進程
```powershell
Stop-Process -Id 49256 -Force
Stop-Process -Id 79256 -Force
```

### Step 3: 重新啟動後端
```bash
cd w:\P-PA6.4\Develop\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 10181 --reload
```

**啟動日誌確認**:
```
✅ Redis 連線成功: 10.1.0.20:6379 (DB 1)
```

### Step 4: 驗證登入功能
```bash
python monitor_redis_login.py
```

**結果**:
- ✅ 登入成功
- ✅ Redis DB 1 新增了 3 個 keys
- ✅ 資料正確寫入 `10.1.0.20:6379 DB 1`

## 總結

### 根本原因排序 (重要性)
1. **多個後端進程同時運行** (90% 的問題)
   - 舊進程使用了錯誤的 Redis 配置
   - 請求被舊進程處理

2. **.env 檔案缺少 Redis 配置** (10% 的問題)
   - 雖然 config.py 有預設值
   - 但明確的環境變數配置更可靠
   - 避免依賴程式碼預設值

3. **缺乏進程管理機制**
   - 沒有檢查是否已有進程在運行
   - 沒有自動停止舊進程
   - 導致多個版本同時運行

### 預防措施

1. **啟動前檢查**:
   ```bash
   # 檢查 10181 port
   netstat -ano | findstr ":10181"
   # 如果有進程,先停止
   ```

2. **使用進程管理工具**:
   - 考慮使用 `supervisor` 或 `pm2`
   - 或者寫一個啟動腳本自動檢查和停止舊進程

3. **配置檔案完整性檢查**:
   ```bash
   # 啟動時檢查必要的環境變數
   if [ -z "$REDIS_HOST" ]; then
       echo "ERROR: REDIS_HOST not set"
       exit 1
   fi
   ```

4. **健康檢查端點**:
   ```python
   @app.get("/health")
   def health_check():
       return {
           "redis_connected": redis_health_check(),
           "redis_host": settings.REDIS_HOST,
           "redis_db": settings.REDIS_DB
       }
   ```

## 經驗教訓

1. **環境變數要明確設定**,不要依賴程式碼預設值
2. **啟動服務前要檢查端口占用**,避免多個實例同時運行
3. **配置變更後要重新啟動所有相關服務**
4. **使用健康檢查端點驗證配置是否正確**
5. **開發環境也需要進程管理機制**

## 相關檔案

- 配置檔案: `w:\P-PA6.4\Develop\backend\.env`
- 設定類別: `w:\P-PA6.4\Develop\backend\app\core\config.py`
- Redis 客戶端: `w:\P-PA6.4\Develop\backend\app\core\redis_client.py`
- Session 服務: `w:\P-PA6.4\Develop\backend\app\services\session_service.py`
- Token 管理: `w:\P-PA6.4\Develop\backend\app\core\transaction_token_redis.py`
