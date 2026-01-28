# Redis 設定指南 - 交易令牌機制必要元件

## 問題診斷

### 症狀
- Redis 中看不到 txn token 的建立
- 系統可能使用記憶體儲存 (fallback 機制)

### 原因
Redis 服務未運行或未安裝

---

## 解決方案

### Windows 環境

#### 方案 1: 安裝 Redis (推薦用於開發環境)

1. **下載 Redis for Windows**
   - 前往: https://github.com/tporadowski/redis/releases
   - 下載最新版本的 `.msi` 安裝檔
   - 或使用 Chocolatey: `choco install redis-64`

2. **安裝並啟動 Redis**
   ```powershell
   # 如果使用 MSI 安裝,服務會自動啟動
   # 檢查服務狀態
   Get-Service Redis*

   # 手動啟動服務
   Start-Service Redis
   ```

3. **驗證 Redis 運行**
   ```powershell
   redis-cli ping
   # 應該回傳: PONG
   ```

4. **查看 Token**
   ```powershell
   # 查看所有 txn_token
   redis-cli KEYS "txn_token:*"

   # 查看所有 session_func_token
   redis-cli KEYS "session_func_token:*"

   # 查看特定 token 的內容
   redis-cli GET "txn_token:YOUR_TOKEN_HASH"
   ```

#### 方案 2: 使用 Docker (推薦用於生產環境)

1. **啟動 Redis 容器**
   ```bash
   docker run -d --name redis -p 6379:6379 redis:latest
   ```

2. **驗證運行**
   ```bash
   docker exec -it redis redis-cli ping
   # 應該回傳: PONG
   ```

3. **查看 Token**
   ```bash
   docker exec -it redis redis-cli KEYS "txn_token:*"
   ```

#### 方案 3: 使用 WSL2 + Redis

```bash
# 在 WSL2 中安裝 Redis
sudo apt update
sudo apt install redis-server

# 啟動 Redis
sudo service redis-server start

# 驗證
redis-cli ping
```

---

## 設定確認

### 1. 檢查 Backend 設定

檢查 `Develop/backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # Redis 設定
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
```

### 2. 檢查 Backend 啟動日誌

啟動 backend 時應該看到:

```
✅ Redis 連線成功: localhost:6379 (DB 0)
✅ 使用 Redis 儲存交易令牌
```

如果看到:
```
❌ Redis 連線失敗: [Errno 111] Connection refused
⚠️  系統將使用記憶體儲存 (不適合生產環境)
⚠️  使用記憶體儲存交易令牌
```

表示 Redis 未運行或連線設定錯誤。

---

## Token 機制驗證步驟

### 1. 啟動 Redis 服務

```powershell
# Windows (如果使用服務)
Start-Service Redis

# 或直接執行
redis-server
```

### 2. 啟動 Backend

```bash
cd Develop/backend
uvicorn app.main:app --reload
```

查看啟動日誌,確認:
```
✅ Redis 連線成功: localhost:6379 (DB 0)
```

### 3. 測試 Token 建立

使用 Postman 或 curl:

```bash
# 1. 登入取得 Bearer Token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your_password"}'

# 回應範例:
# {"access_token": "eyJhbGciOiJIUzI1NiIs...", ...}

# 2. 申請交易令牌
curl -X POST http://localhost:8000/api/transaction/request \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"func_code": "user_roles"}'

# 回應範例:
# {
#   "txn_token": "abc123def456...",
#   "expires_in": 1800,
#   "func_code": "user_roles",
#   "permissions": {
#     "create": true,
#     "read": true,
#     "update": true,
#     "delete": true,
#     "print": false,
#     "file": false
#   }
# }
```

### 4. 檢查 Redis

```powershell
# 查看所有 token keys
redis-cli KEYS "*"

# 應該看到:
# 1) "txn_token:abc123def456..."
# 2) "session_func_token:eyJhbGciOiJIUzI1NiIs...:5"

# 查看 token 內容
redis-cli GET "txn_token:abc123def456..."

# 應該看到 JSON 格式的 token 資訊:
# {
#   "session_id": "eyJhbGciOiJIUzI1NiIs...",
#   "system_functions_id": 5,
#   "permissions": {
#     "create": true,
#     "read": true,
#     ...
#   },
#   "created_at": "2026-01-26T10:00:00+08:00",
#   "last_access": "2026-01-26T10:00:00+08:00"
# }

# 查看 TTL (剩餘時間)
redis-cli TTL "txn_token:abc123def456..."
# 應該顯示秒數，例如: 1799 (約 30 分鐘)
```

### 5. 測試 API 呼叫

```bash
# 使用 txn_token 呼叫 API
curl -X GET http://localhost:8000/api/user_roles \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Txn-Token: YOUR_TXN_TOKEN"

# 應該成功回傳資料
```

---

## 常見問題

### Q1: Redis 連線失敗

**症狀**: Backend 啟動時顯示 "Redis 連線失敗"

**解決**:
1. 確認 Redis 服務正在運行
2. 檢查防火牆設定
3. 確認 REDIS_HOST 和 REDIS_PORT 正確

### Q2: Token 建立但看不到

**症狀**: API 回應正常但 Redis 中沒有 key

**解決**:
1. 確認使用正確的 Redis DB (預設是 DB 0)
   ```bash
   redis-cli -n 0 KEYS "*"
   ```
2. 檢查 Backend 日誌是否有錯誤

### Q3: Token 過期太快

**症狀**: Token 很快就失效

**檢查**:
- Token 有效期應該是 30 分鐘 (1800 秒)
- 使用 `redis-cli TTL key` 檢查實際 TTL

---

## Fallback 記憶體模式

如果 Redis 無法使用,系統會自動切換到記憶體儲存模式:

### 優點
- 不需要 Redis,開發更簡單
- 邏輯完全相同

### 缺點
- ❌ **不適合生產環境**
- ❌ Backend 重啟後 Token 全部失效
- ❌ 多個 Backend 實例無法共享 Token
- ❌ 無法持久化

### 使用場景
- ✅ 本機開發測試
- ❌ 生產環境 (必須使用 Redis)

---

## 生產環境建議

1. **使用 Redis 持久化**
   ```
   # redis.conf
   save 900 1
   save 300 10
   save 60 10000
   ```

2. **使用 Redis Sentinel 或 Cluster**
   - 高可用性
   - 自動故障轉移

3. **監控 Redis**
   - 記憶體使用量
   - 連線數
   - 命中率

4. **設定 Redis 密碼**
   ```python
   REDIS_PASSWORD = "your_strong_password"
   ```

---

**最後更新**: 2026-01-26
**維護者**: 開發團隊
