# PA6.4 系統文件索引

## 核心設計文件

### 架構設計
- **[SIMPLIFIED_ARCHITECTURE_DESIGN.md](SIMPLIFIED_ARCHITECTURE_DESIGN.md)** - 簡化架構設計
  - 系統架構概覽
  - 技術選型
  - 模組劃分

### 多租戶設計
- **[ORG_ID_DESIGN.md](ORG_ID_DESIGN.md)** - org_id 設計說明
  - 多租戶概念
  - 資料隔離機制
  - 使用範例

### 權限系統
- **[TWO_TIER_PERMISSION_ARCHITECTURE.md](TWO_TIER_PERMISSION_ARCHITECTURE.md)** - 雙層權限架構
  - 功能權限 + 操作權限
  - RBAC 實作
  - 權限檢查流程

### Schema 設計
- **[SCHEMA_DESIGN_GUIDELINES.md](SCHEMA_DESIGN_GUIDELINES.md)** - Schema 設計指導原則
  - Create/Update Schema 設計原則
  - 安全性考量
  - 檢查清單

### 命名規範
- **[NAMING_STANDARDS.md](NAMING_STANDARDS.md)** - 命名標準
  - 資料表命名
  - API 路由命名
  - 前端檔案命名

### 錯誤處理
- **[ERROR_HANDLING_IMPROVEMENT.md](ERROR_HANDLING_IMPROVEMENT.md)** - 錯誤處理改善
  - 結構化錯誤回應
  - 前端錯誤解析
  - 日誌記錄

## 環境與部署

### 開發環境
- **[DEVELOPMENT_ENVIRONMENT.md](DEVELOPMENT_ENVIRONMENT.md)** - 開發測試環境配置
  - PostgreSQL 和 Redis 設定 (10.1.0.20)
  - Frontend Port 10180 / Backend Port 10181
  - 快速啟動指令
  - 環境變數設定

### 部署策略
- **[guides/DEPLOYMENT_STRATEGY.md](guides/DEPLOYMENT_STRATEGY.md)** - 環境區分與部署策略
  - 三層環境架構 (開發/測試/營運)
  - 原始碼保護策略 (Cython .so 編譯)
  - Docker 部署設定
  - 環境變數管理

## 開發指南

### 交易令牌
- **[guides/TRANSACTION_TOKEN_GUIDE.md](guides/TRANSACTION_TOKEN_GUIDE.md)** - 交易令牌使用指南
  - Token v3.0 機制
  - 使用方式
  - 延長機制

### 功能開發
- **[guides/FEATURE_DEVELOPMENT_TEMPLATE.md](guides/FEATURE_DEVELOPMENT_TEMPLATE.md)** - 功能開發範本
  - 開發流程
  - 程式碼範本
  - 檢查清單

### 新專案啟動
- **[guides/NEW_PROJECT_SETUP.md](guides/NEW_PROJECT_SETUP.md)** - 使用範本建立新專案指南
  - 複製專案步驟
  - 必須修改的配置
  - 同時運行多個專案

## 完成報告

### Token 機制
- **[TOKEN_V3_DOCUMENTATION_UPDATE.md](TOKEN_V3_DOCUMENTATION_UPDATE.md)** - Token v3.0 完成報告
- **[TOKEN_MECHANISM_V2_COMPLETE.md](TOKEN_MECHANISM_V2_COMPLETE.md)** - Token v2.0 完成報告

### 資料庫遷移
- **[POSTGRESQL_MIGRATION_COMPLETE.md](POSTGRESQL_MIGRATION_COMPLETE.md)** - PostgreSQL 遷移完成
- **[SCHEMA_RENAMING_COMPLETE.md](SCHEMA_RENAMING_COMPLETE.md)** - Schema 重新命名完成

### 功能完成
- **[SYSTEM_NOTIFICATIONS_COMPLETE.md](SYSTEM_NOTIFICATIONS_COMPLETE.md)** - 系統通知功能完成
- **[I18N_TRANSLATIONS_COMPLETE.md](I18N_TRANSLATIONS_COMPLETE.md)** - 多語系翻譯完成

### 功能移除
- **[REMOVE_NUMBERING_RULES_FEATURE.md](REMOVE_NUMBERING_RULES_FEATURE.md)** - 編號規則功能移除記錄

## 歷史記錄

### 問題修正
- **[history/FIX_MYPROFILE_EDIT_BUTTON_ISSUE.md](history/FIX_MYPROFILE_EDIT_BUTTON_ISSUE.md)** - 個人資料編輯按鈕修正
- **[history/FIX_TOKEN_ISSUE.md](history/FIX_TOKEN_ISSUE.md)** - Token 問題修正
- **[history/REDIS_ISSUE_ROOT_CAUSE.md](history/REDIS_ISSUE_ROOT_CAUSE.md)** - Redis 問題根因分析

### 重構記錄
- **[history/SESSION_ID_REFACTORING_PLAN.md](history/SESSION_ID_REFACTORING_PLAN.md)** - Session ID 重構計畫
- **[history/TRANSACTION_TOKEN_TROUBLESHOOT.md](history/TRANSACTION_TOKEN_TROUBLESHOOT.md)** - 交易令牌問題排查
- **[history/TXN_TOKEN_BUG_FIX_COMPLETE.md](history/TXN_TOKEN_BUG_FIX_COMPLETE.md)** - Token Bug 修正完成
- **[history/TXN_TOKEN_FIX_VERIFICATION.md](history/TXN_TOKEN_FIX_VERIFICATION.md)** - Token 修正驗證

## 快速導航

### 我想要...

**了解系統架構**
→ [SIMPLIFIED_ARCHITECTURE_DESIGN.md](SIMPLIFIED_ARCHITECTURE_DESIGN.md)

**開發新功能**
→ [guides/FEATURE_DEVELOPMENT_TEMPLATE.md](guides/FEATURE_DEVELOPMENT_TEMPLATE.md)

**使用交易令牌**
→ [guides/TRANSACTION_TOKEN_GUIDE.md](guides/TRANSACTION_TOKEN_GUIDE.md)

**使用範本建立新專案**
→ [guides/NEW_PROJECT_SETUP.md](guides/NEW_PROJECT_SETUP.md)

**設計資料表 Schema**
→ [SCHEMA_DESIGN_GUIDELINES.md](SCHEMA_DESIGN_GUIDELINES.md)

**了解 org_id 設計**
→ [ORG_ID_DESIGN.md](ORG_ID_DESIGN.md)

**部署系統**
→ [guides/DEPLOYMENT_GUIDE.md](guides/DEPLOYMENT_GUIDE.md)

**查看更新歷史**
→ [../../CHANGELOG.md](../../CHANGELOG.md)

---

**最後更新**: 2026-01-29
