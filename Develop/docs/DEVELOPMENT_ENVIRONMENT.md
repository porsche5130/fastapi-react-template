# 開發測試環境配置

## 專案資訊
- **專案名稱**: Paris Agreement Article 6.4 管理系統
- **專案代碼**: PA6.4
- **文件版本**: 1.6.0
- **最後更新**: 2026-01-28

---

## 快速參考 - 連線資訊

### PostgreSQL (遠端固定環境)
```
Host:     10.1.0.20
Port:     5433
Database: pa64_dev
User:     admin
Password: !DC1qaz2wsx

連線字串:
postgresql://admin:!DC1qaz2wsx@10.1.0.20:5433/pa64_dev
```

### Redis (遠端固定環境)
```
Host:     10.1.0.20
Port:     6379
Database: 1 (PA6.4 專用)
Password: !DC1qaz2wsx

連線字串:
redis://:!DC1qaz2wsx@10.1.0.20:6379/1
```

### 本機服務 Port
```
Frontend:  http://localhost:10180
Backend:   http://localhost:10181
API Docs:  http://localhost:10181/docs
```

---

## 一、環境架構概覽

```
本機開發環境
├── PostgreSQL (遠端伺服器)
│   ├── Host: 10.1.0.20
│   ├── Port: 5433
│   ├── Database: pa64_dev
│   ├── User: admin
│   └── Password: !DC1qaz2wsx
│
├── Redis (遠端伺服器)
│   ├── Host: 10.1.0.20
│   ├── Port: 6379
│   ├── Database: 1 (PA6.4 專用)
│   ├── 認證: 密碼驗證
│   └── Password: !DC1qaz2wsx
│
└── 應用服務 (W:\P-PA6.4\Develop)
    ├── Frontend (React + Vite)
    │   ├── 位置: W:\P-PA6.4\Develop\frontend
    │   ├── Port: 10180
    │   └── API Proxy: /api → http://localhost:10181
    │
    └── Backend (FastAPI)
        ├── 位置: W:\P-PA6.4\Develop\backend
        ├── Port: 10181
        └── 可透過 http://localhost:10180/api 存取
```

### Port 配置說明

| 服務 | Port | 用途 | 存取方式 |
|------|------|------|----------|
| **Frontend** | 10180 | 前端開發伺服器 | http://localhost:10180 |
| **Backend** | 10181 | 後端 API 伺服器 | http://localhost:10181 |
| **API (透過前端)** | 10180/api | 前端代理後端 API | http://localhost:10180/api |
| **PostgreSQL** | 5433 | 資料庫 | 10.1.0.20:5433 |
| **Redis** | 6379 | 快取/會話 | 10.1.0.20:6379 (DB 1) |

---

## 二、PostgreSQL 環境

### 2.1 基本資訊

| 項目 | 內容 |
|------|------|
| **安裝位置** | 遠端伺服器 (10.1.0.20) |
| **版本** | PostgreSQL 16.11 |
| **主機** | 10.1.0.20 |
| **Port** | 5433 |
| **資料庫名稱** | pa64_dev |
| **使用者** | admin |
| **密碼** | !DC1qaz2wsx |
| **最大連線數** | 100 |
| **資料量** | 14 個表, 1681 筆資料 |

### 2.2 連線字串

#### **遠端連線 (預設)**
```
postgresql://admin:!DC1qaz2wsx@10.1.0.20:5433/pa64_dev
```

#### **本機測試連線 (已停用)**
```
# 本機 PostgreSQL 已移轉至遠端伺服器
# postgresql://dev:dev123@localhost:5432/pa64_dev
```

### 2.3 資料遷移記錄

**遷移日期**: 2026-01-28

**來源**: localhost:5432/pa64_dev (本機開發環境)
**目標**: 10.1.0.20:5433/pa64_dev (遠端固定環境)

**遷移內容**:
- 14 個資料表
- 1,681 筆資料
- 13 個序列
- 24 個外鍵約束
- 55 個索引

**驗證狀態**: ✅ 所有資料完整遷移,功能正常運作

### 2.4 測試驗證

#### **連線測試**
```bash
# 使用 admin 使用者測試遠端連線
psql -h 10.1.0.20 -p 5433 -U admin -d pa64_dev -c "SELECT version();"

# 或使用 Python 測試
python test_postgres_remote.py
```

#### **功能測試**
```bash
# 執行遷移驗證腳本
cd W:\P-PA6.4
python verify_migration.py
```

#### **測試結果（2026-01-28）**
```
✓ 連線測試 - 成功（遠端 10.1.0.20:5433）
✓ 版本檢查 - PostgreSQL 16.11
✓ 資料表數量 - 14 個（與本機一致）
✓ 資料筆數 - 1,681 筆（完全相同）
✓ 序列值 - 正確設定
✓ JSONB 資料 - 正常運作
✓ 外鍵關聯 - 完整保留
✓ 最大連線數 - 100
```

---

## 三、Redis 環境

### 3.1 基本資訊

| 項目 | 內容 |
|------|------|
| **安裝位置** | 遠端伺服器 |
| **主機** | 10.1.0.20 |
| **Port** | 6379 |
| **版本** | 8.4.0 |
| **認證方式** | 密碼驗證（password-only） |
| **密碼** | !DC1qaz2wsx |
| **資料庫數量** | 16 (db0 - db15) |
| **PA6.4 使用** | DB 1 |

### 3.2 連線字串

#### **開發環境連線 (PA6.4 使用 DB 1)**
```
redis://:!DC1qaz2wsx@10.1.0.20:6379/1
```

#### **其他資料庫**
```
# DB 0 (保留給其他用途)
redis://:!DC1qaz2wsx@10.1.0.20:6379/0

# DB 2-15 (可用於其他專案)
redis://:!DC1qaz2wsx@10.1.0.20:6379/2
```

### 3.3 資料庫分配

使用不同的資料庫編號區分專案：

| 資料庫 | 專案 | 連線字串 | 用途 |
|--------|------|---------|------|
| **db0** | 保留 | `redis://:!DC1qaz2wsx@10.1.0.20:6379/0` | 可用於其他專案 |
| **db1** | **PA6.4** | `redis://:!DC1qaz2wsx@10.1.0.20:6379/1` | **Session、Token、快取** |
| **db2** | 其他專案 | `redis://:!DC1qaz2wsx@10.1.0.20:6379/2` | 可用於其他專案 |
| **db3-15** | 保留 | - | 未來使用 |

### 3.4 測試驗證

#### **連線測試**
```python
import redis

# 連線到 PA6.4 專用的 DB 1
r = redis.Redis(
    host='10.1.0.20',
    port=6379,
    password='!DC1qaz2wsx',
    db=1,  # PA6.4 使用 DB 1
    decode_responses=True
)

# PING 測試
print(r.ping())  # True

# 寫入測試
r.set('test', 'Hello Redis', ex=60)
print(r.get('test'))  # Hello Redis

# 查看伺服器資訊
info = r.info()
print(f"Redis 版本: {info['redis_version']}")
print(f"記憶體使用: {info['used_memory_human']}")
```

#### **基本操作**
```bash
# PING 測試 (連線到遠端 Redis)
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" ping
# 返回: PONG

# 連線到 PA6.4 的 DB 1
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" -n 1

# 查看 PA6.4 的所有 key
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" -n 1 KEYS "*"

# 查看 PA6.4 的 session 相關 key
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" -n 1 KEYS "session:*"

# 查看 PA6.4 的 token 相關 key
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" -n 1 KEYS "txn_token:*"
```

#### **測試結果（2026-01-28）**
```
✓ PING 測試 - True
✓ 寫入測試 - 成功
✓ 讀取測試 - 成功
✓ TTL 設定 - 成功（60秒）
✓ 資料庫切換 - 成功（PA6.4 使用 DB 1）
✓ 清理測試 - 成功
✓ 遠端連線 - 成功（10.1.0.20:6379）
```

**伺服器資訊：**
- Redis 版本：8.4.0
- 伺服器位置：10.1.0.20
- PA6.4 使用：DB 1
- 可用資料庫：16 個（db0-db15）
- 認證方式：密碼驗證（password-only）
- 網路延遲：1-2ms（本地網路）

---

## 四、前後端服務配置

### 4.1 Frontend 開發伺服器 (Vite)

**Port**: 10180

**vite.config.ts**:

**位置**: `W:\P-PA6.4\Develop\frontend\vite.config.ts`

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 10180,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:10181',
        changeOrigin: true
      },
      '/images': {
        target: 'http://localhost:10181',
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://localhost:10181',
        changeOrigin: true
      },
      '/locales': {
        target: 'http://localhost:10181',
        changeOrigin: true
      }
    }
  }
});
```

**存取方式**:
- 前端應用: http://localhost:10180
- API 呼叫: http://localhost:10180/api (自動代理到後端 10181)

### 4.2 Backend 開發伺服器 (FastAPI + Uvicorn)

**Port**: 10181

**啟動指令**:
```bash
cd W:\P-PA6.4\Develop\backend
uvicorn app.main:app --host 0.0.0.0 --port 10181 --reload
```

**backend/.env**:

**位置**: `W:\P-PA6.4\Develop\backend\.env`

```bash
# 應用程式
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG

# 服務 Port
PORT=10181

# 資料庫 (遠端 PostgreSQL)
DATABASE_URL=postgresql://admin:!DC1qaz2wsx@10.1.0.20:5433/pa64_dev

# Redis (遠端 Redis, DB 1)
REDIS_HOST=10.1.0.20
REDIS_PORT=6379
REDIS_DB=1
REDIS_PASSWORD=!DC1qaz2wsx

# 安全性
SECRET_KEY=dev-secret-key-change-in-production

# CORS
ALLOWED_ORIGINS=["http://localhost:10180"]
```

**存取方式**:
- 直接存取: http://localhost:10181
- 透過前端代理: http://localhost:10180/api

### 4.3 API 路由設計

| 前端呼叫 | 代理後實際路徑 | 用途 |
|----------|----------------|------|
| `http://localhost:10180/api/users` | `http://localhost:10181/api/users` | API 端點 |
| `http://localhost:10180/images/logo.svg` | `http://localhost:10181/images/logo.svg` | 圖片資源 |
| `http://localhost:10180/uploads/{file}` | `http://localhost:10181/uploads/{file}` | 上傳檔案 |
| `http://localhost:10180/locales/zh-TW/common.json` | `http://localhost:10181/locales/zh-TW/common.json` | 語系檔案 |

---

## 五、環境啟動流程

### 5.1 前置檢查

```bash
# 1. 檢查 PostgreSQL (遠端伺服器 10.1.0.20:5433)
psql -h 10.1.0.20 -p 5433 -U admin -d pa64_dev -c "SELECT version();"
# 密碼: !DC1qaz2wsx

# 2. 檢查 Redis (遠端伺服器 10.1.0.20:6379 DB 1)
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" -n 1 ping

# 3. 檢查前端依賴
cd W:\P-PA6.4\Develop\frontend
npm install

# 4. 檢查後端依賴
cd W:\P-PA6.4\Develop\backend
pip install -r requirements.txt
```

### 5.2 啟動服務

**終端機 1 - 啟動後端**:
```bash
cd W:\P-PA6.4\Develop\backend
uvicorn app.main:app --host 0.0.0.0 --port 10181 --reload
```

**終端機 2 - 啟動前端**:
```bash
cd W:\P-PA6.4\Develop\frontend
npm run dev
```

### 5.3 驗證服務

| 服務 | URL | 說明 |
|------|-----|------|
| **前端** | http://localhost:10180 | React 開發伺服器 (Vite) |
| **後端** | http://localhost:10181 | FastAPI 服務 |
| **API 文件** | http://localhost:10181/docs | Swagger UI |
| **前端 API 代理** | http://localhost:10180/api | 透過前端代理的後端 API |

---

## 六、優點說明

### 6.1 遠端固定環境的優勢

1. **即時熱重載**
   - Vite 提供極快的 HMR (Hot Module Replacement)
   - Uvicorn `--reload` 偵測 Python 檔案變更自動重啟
   - 修改程式碼後立即生效

2. **除錯方便**
   - 可直接使用 IDE 的偵錯工具 (VSCode, PyCharm)
   - 設定中斷點 (Breakpoint)
   - 即時查看變數狀態

3. **資源節省**
   - 不需要為開發環境建置 Docker Image
   - PostgreSQL 和 Redis 運行在遠端固定環境
   - 本機只需運行前後端程式

4. **環境一致性**
   - 固定的 PostgreSQL 和 Redis 環境
   - 所有開發者使用相同的資料庫配置
   - 減少「在我的電腦上可以運作」問題

5. **資料持久化與共享**
   - 資料存在遠端伺服器,不受本機環境影響
   - 團隊成員可共享開發資料
   - 方便備份和恢復

6. **快速切換**
   - 不同專案間快速切換 Port
   - 不需要重建 Docker 容器
   - Redis 使用不同 DB 編號隔離專案資料

---

## 七、注意事項

### 7.1 Port 衝突

確保 Port 10180 和 10181 沒有被其他程式佔用：

```bash
# Windows 檢查 Port 佔用
netstat -ano | findstr :10180
netstat -ano | findstr :10181

# 如果被佔用，終止程式
taskkill /PID <PID> /F
```

### 7.2 資料庫連線

開發環境資料庫配置：

```bash
# PostgreSQL (遠端固定環境)
DATABASE_URL=postgresql://admin:!DC1qaz2wsx@10.1.0.20:5433/pa64_dev

# Redis (遠端固定環境, DB 1)
REDIS_HOST=10.1.0.20
REDIS_PORT=6379
REDIS_DB=1
REDIS_PASSWORD=!DC1qaz2wsx
```

**重要提醒**：
- PostgreSQL：使用 `10.1.0.20:5433` (遠端固定環境)
- Redis：使用 `10.1.0.20:6379` (遠端固定環境)
- PA6.4 專用 Redis DB 1，請勿與其他專案混用
- 所有開發者使用相同的遠端環境配置

### 7.3 環境變數檔案

開發環境的 `.env` 檔案**絕對不可提交到 Git**：

```bash
# 確認 .gitignore 包含
.env
.env.local
.env.*.local
__pycache__/
node_modules/
```

### 7.4 依賴更新

當 `package.json` 或 `requirements.txt` 更新時：

```bash
# Frontend
cd W:\P-PA6.4\Develop\frontend
npm install

# Backend
cd W:\P-PA6.4\Develop\backend
pip install -r requirements.txt
```

### 7.5 資料庫連線數

- PostgreSQL 最大連線數: 100 (遠端環境)
- Redis 預設最大連線數: 10000
- 多專案共用時注意連線池設定
- 建議後端使用連線池管理資料庫連線

---

## 八、故障排除

### 8.1 PostgreSQL 連線失敗

```bash
# 檢查遠端服務是否運行
psql -h 10.1.0.20 -p 5433 -U admin -d pa64_dev -c "SELECT 1;"
# 密碼: !DC1qaz2wsx

# 檢查網路連通性
ping 10.1.0.20

# 檢查端口是否開放
powershell -Command "Test-NetConnection -ComputerName 10.1.0.20 -Port 5433"

# 測試 Python 連線
python -c "import psycopg2; conn=psycopg2.connect('postgresql://admin:!DC1qaz2wsx@10.1.0.20:5433/pa64_dev'); print('OK')"
```

### 8.2 Redis 連線失敗

```bash
# 檢查遠端 Redis 服務是否運行
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" ping

# 檢查網路連通性
ping 10.1.0.20

# 檢查端口是否開放
powershell -Command "Test-NetConnection -ComputerName 10.1.0.20 -Port 6379"

# 測試 Python 連線
python -c "import redis; r=redis.Redis(host='10.1.0.20', port=6379, db=1, password='!DC1qaz2wsx'); print(r.ping())"
```

### 8.3 遠端服務連線問題

可能原因：
1. 防火牆阻擋 (檢查 10.1.0.20 的防火牆設定)
2. 網路連線問題 (使用 ping 測試)
3. 服務未啟動 (聯繫管理員確認服務狀態)
4. 帳號密碼錯誤 (確認使用正確的認證資訊)

---

## 九、附錄

### 9.1 快速指令參考

```bash
# Frontend (Vite)
cd W:\P-PA6.4\Develop\frontend
npm run dev                                             # 啟動開發伺服器 (Port 10180)
npm run build                                           # 建置生產版本

# Backend (FastAPI)
cd W:\P-PA6.4\Develop\backend
uvicorn app.main:app --host 0.0.0.0 --port 10181 --reload  # 啟動開發伺服器
python -m pytest                                        # 執行測試

# PostgreSQL (遠端 10.1.0.20:5433, admin/!DC1qaz2wsx)
psql -h 10.1.0.20 -p 5433 -U admin -d pa64_dev                    # 連線
pg_dump -h 10.1.0.20 -p 5433 -U admin pa64_dev > backup.sql       # 備份
psql -h 10.1.0.20 -p 5433 -U admin -d pa64_dev < backup.sql       # 還原

# Redis (遠端伺服器 10.1.0.20)
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" -n 1                    # 連線 PA6.4 的 DB 1
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" -n 1 --scan --pattern "session:*"    # 查找 session key
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" -n 1 --scan --pattern "txn_token:*"  # 查找 token key
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" -n 1 DBSIZE             # 查看 key 數量
redis-cli -h 10.1.0.20 -a "!DC1qaz2wsx" -n 1 INFO memory        # 查看記憶體使用

# Docker
docker-compose -f docker-compose.dev.yml up -d          # 啟動
docker-compose -f docker-compose.dev.yml down           # 停止
docker-compose -f docker-compose.dev.yml logs -f        # 日誌
```

### 9.2 測試與遷移腳本

**資料庫遷移腳本**：
```
W:\P-PA6.4\
├── create_remote_database.py      # 建立遠端資料庫
├── migrate_db_complete.py         # 完整資料庫遷移工具
├── verify_migration.py            # 驗證遷移結果
├── test_postgres_remote.py        # PostgreSQL 遠端連線測試
├── test_pg_admin.py               # PostgreSQL admin 帳號測試
└── test_redis_pwd.py              # Redis 密碼認證測試
```

**執行測試：**
```bash
# PostgreSQL 連線測試
cd W:\P-PA6.4
python test_postgres_remote.py

# 驗證資料庫遷移結果
python verify_migration.py

# Redis 連線測試
python test_redis_pwd.py
```

---

## 十、更新記錄

| 日期 | 版本 | 說明 |
|------|------|------|
| 2026-01-18 | 1.0.0 | 建立初始文檔，記錄 PostgreSQL 和 Redis 環境配置 |
| 2026-01-18 | 1.1.0 | 完成 PostgreSQL 和 Redis 實際測試，更新版本資訊和測試結果 |
| 2026-01-18 | 1.2.0 | 新增前後端 Port 配置（前端 10180、後端 10181），設定 API 代理 |
| 2026-01-18 | 1.3.0 | 更新開發環境目錄為 W:\P-PA6.4\Develop，統一所有路徑參照 |
| 2026-01-18 | 1.4.0 | 修正 5.2、5.3 為本機直接執行（非 Docker），更新 Port 為 10180/10181，調整注意事項 |
| 2026-01-28 | 1.5.0 | 更新 Redis 配置為遠端伺服器 10.1.0.20，PA6.4 使用 DB 1，版本更新為 8.4.0 |
| 2026-01-28 | 1.6.0 | PostgreSQL 遷移至遠端固定環境 10.1.0.20:5433，更新所有配置和測試說明 |
