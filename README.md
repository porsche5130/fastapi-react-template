# PA6.4 管理系統

企業級多租戶管理系統,提供組織管理、使用者管理、權限控制、系統設定等核心功能。

## 系統資訊

- **版本**: v1.0.0
- **開發環境**: PostgreSQL + Redis + FastAPI + React 19
- **架構**: 前後端分離、多租戶隔離、交易令牌機制

## 主要功能

### 系統管理
- 系統設定檔維護
- 系統功能管理
- 系統代碼維護
- 系統通知管理

### 組織管理
- 組織資料維護
- 用戶端資料維護
- 檔案附件管理

### 權限管理
- 使用者角色管理
- 角色權限設定
- 使用者管理
- 使用者日誌查詢

### 個人功能
- 個人資料變更
- 密碼變更

## 技術架構

### Backend
- **框架**: FastAPI 0.104+
- **資料庫**: PostgreSQL 14+
- **快取**: Redis 7+
- **ORM**: SQLAlchemy 2.0+
- **驗證**: JWT + Redis Session

### Frontend
- **框架**: React 19+
- **語言**: TypeScript 5+
- **UI**: Ant Design 5+
- **路由**: React Router v6
- **狀態**: Context API
- **多語系**: i18next

## 快速開始

### 環境需求

- Python 3.13+
- Node.js 20+
- PostgreSQL 14+
- Redis 7+

### 安裝步驟

1. **Clone 專案**
```bash
git clone <repository-url>
cd P-PA6.4
```

2. **設定 Backend**
```bash
cd Develop/backend
pip install -r requirements.txt
cp .env.example .env
# 編輯 .env 設定資料庫連線
```

3. **初始化資料庫**
```bash
# 執行資料庫 migrations
cd migrations
python run_migration_auto.py
```

4. **設定 Frontend**
```bash
cd ../frontend
npm install
```

5. **啟動服務**

Backend:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 10181 --reload
```

Frontend:
```bash
cd frontend
npm run dev
```

6. **訪問系統**
- Frontend: http://localhost:10180
- Backend API: http://localhost:10181
- API 文件: http://localhost:10181/docs

### 預設帳號

```
帳號: admin@example.com
密碼: admin123
```

## 專案結構

```
P-PA6.4/
├── Develop/
│   ├── backend/              # FastAPI 後端
│   │   ├── app/
│   │   │   ├── core/        # 核心功能 (資料庫、Redis、設定)
│   │   │   ├── models/      # SQLAlchemy Models
│   │   │   ├── schemas/     # Pydantic Schemas
│   │   │   ├── routes/      # API 路由
│   │   │   └── main.py      # 應用程式入口
│   │   ├── migrations/      # 資料庫遷移腳本
│   │   └── requirements.txt
│   │
│   ├── frontend/            # React 前端
│   │   ├── src/
│   │   │   ├── components/  # React 元件
│   │   │   ├── contexts/    # Context Providers
│   │   │   ├── pages/       # 頁面元件
│   │   │   ├── services/    # API Services
│   │   │   ├── hooks/       # Custom Hooks
│   │   │   ├── types/       # TypeScript 類型
│   │   │   └── locales/     # 多語系資源
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   └── docs/                # 文件
│       ├── guides/          # 開發指南
│       └── history/         # 歷史記錄
│
└── 系統設計/                # 系統設計文件
```

## 核心設計

### 多租戶架構 (Multi-tenancy)

系統使用 `org_id` 實現資料隔離:

- 每個組織擁有獨立的資料空間
- 查詢時自動過濾當前使用者的組織資料
- 建立資料時自動填入使用者的組織 ID

詳見: [Develop/docs/ORG_ID_DESIGN.md](Develop/ORG_ID_DESIGN.md)

### 交易令牌機制 (Transaction Token v3.0)

- 每個 Session 一個 Token,包含所有功能權限
- Token 存儲在 Redis,有效期 30 分鐘
- 支援延長機制,持續操作自動延長
- 防止併發問題和權限繞過

詳見: [Develop/docs/guides/TRANSACTION_TOKEN_GUIDE.md](Develop/docs/guides/TRANSACTION_TOKEN_GUIDE.md)

### 權限控制

- 雙層權限架構: 功能權限 + 操作權限
- 基於角色的存取控制 (RBAC)
- 細粒度權限控制 (create/read/update/delete/print/file)

詳見: [Develop/docs/TWO_TIER_PERMISSION_ARCHITECTURE.md](Develop/docs/TWO_TIER_PERMISSION_ARCHITECTURE.md)

## 開發指南

### Schema 設計原則

- Create/Update Schema **不應包含**後端自動填入的欄位
- `org_id`, `created_by`, `updated_by` 等由後端明確指定
- 防止安全漏洞 (使用者偽造組織 ID)

詳見: [Develop/docs/SCHEMA_DESIGN_GUIDELINES.md](Develop/docs/SCHEMA_DESIGN_GUIDELINES.md)

### 命名規範

- 資料表: 小寫 + 底線 (例: `user_roles`)
- Model: PascalCase (例: `UserRole`)
- API 路由: 小寫 + 連字號 (例: `/api/user-roles`)
- 前端檔案: PascalCase (例: `UserRolesPage.tsx`)

詳見: [Develop/docs/NAMING_STANDARDS.md](Develop/docs/NAMING_STANDARDS.md)

### 新功能開發

使用功能開發範本快速建立新功能:

詳見: [Develop/docs/guides/FEATURE_DEVELOPMENT_TEMPLATE.md](Develop/docs/guides/FEATURE_DEVELOPMENT_TEMPLATE.md)

## 部署指南

### 開發環境

```bash
# 使用提供的啟動腳本
start_dev_environment.bat
```

### 生產環境

詳見: [Develop/docs/guides/DEPLOYMENT_GUIDE.md](Develop/docs/guides/DEPLOYMENT_GUIDE.md)

## 重要文件

### 設計文件
- [系統架構設計](Develop/docs/SIMPLIFIED_ARCHITECTURE_DESIGN.md)
- [org_id 設計說明](Develop/docs/ORG_ID_DESIGN.md)
- [權限系統架構](Develop/docs/TWO_TIER_PERMISSION_ARCHITECTURE.md)

### 開發指南
- [交易令牌使用指南](Develop/docs/guides/TRANSACTION_TOKEN_GUIDE.md)
- [Schema 設計指導](Develop/docs/SCHEMA_DESIGN_GUIDELINES.md)
- [錯誤處理改善](Develop/docs/ERROR_HANDLING_IMPROVEMENT.md)

### 完成報告
- [系統通知功能完成](Develop/docs/SYSTEM_NOTIFICATIONS_COMPLETE.md)
- [PostgreSQL 遷移完成](Develop/docs/POSTGRESQL_MIGRATION_COMPLETE.md)
- [Token v3.0 完成](Develop/docs/TOKEN_V3_DOCUMENTATION_UPDATE.md)

## 維護記錄

### 已移除的功能

- **編號規則功能** (2026-01-29): 屬於客製化功能,應依專案需求客製開發
  - 詳見: [REMOVE_NUMBERING_RULES_FEATURE.md](Develop/docs/history/REMOVE_NUMBERING_RULES_FEATURE.md)

## 版本歷史

### v1.0.0 (2026-01-29)
- ✅ 完成核心功能開發
- ✅ 完成 PostgreSQL + Redis 整合
- ✅ 完成交易令牌機制 v3.0
- ✅ 完成多語系支援 (繁中/英文)
- ✅ 完成系統通知功能
- ✅ 移除非基底功能 (編號規則)

## 授權

Copyright © 2026 匠耘公司

## 聯絡方式

- **開發團隊**: Claude Code
- **專案管理**: 匠耘公司

---

**最後更新**: 2026-01-29
