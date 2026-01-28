# 更新日誌

本專案的所有重要變更都會記錄在此文件中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/),
版本號碼使用 [語意化版本](https://semver.org/lang/zh-TW/)。

## [1.0.0] - 2026-01-29

### 新增功能 (Added)

#### 系統管理
- ✅ 系統設定檔維護 (sys_profiles)
- ✅ 系統功能管理 (system_functions)
- ✅ 系統代碼維護 (system_codes)
- ✅ 系統通知管理 (system_notifications)
  - 支援 Markdown 富文本編輯
  - 支援通知關閉日期設定
  - 已讀/未讀狀態追蹤

#### 組織管理
- ✅ 組織資料維護 (organizations)
- ✅ 用戶端資料維護 (tenant_users)
  - 完整的 CRUD 功能
  - Modal 彈窗編輯介面
  - 資料驗證和錯誤處理
- ✅ 檔案附件管理 (file_attachments)

#### 權限管理
- ✅ 使用者角色管理 (user_roles)
- ✅ 角色權限設定 (role_rights)
  - 雙層權限架構 (功能 + 操作)
  - 細粒度權限控制 (create/read/update/delete/print/file)
- ✅ 使用者管理 (users)
- ✅ 使用者日誌查詢 (user_logs)

#### 個人功能
- ✅ 個人資料變更 (my_profile)
- ✅ 密碼變更 (change_password)

#### 技術架構
- ✅ 多租戶架構 (Multi-tenancy)
  - org_id 資料隔離
  - 自動過濾組織資料
- ✅ 交易令牌機制 v3.0
  - 一個 Session 一個 Token
  - Token 包含所有功能權限
  - 自動延長機制
  - 防止併發和權限繞過
- ✅ 多語系支援
  - 繁體中文 (zh-TW)
  - 英文 (en)
- ✅ 結構化錯誤處理
  - error_code + message + details
  - 前端錯誤解析和顯示
  - 使用者日誌記錄

### 變更 (Changed)

#### 資料庫遷移
- 🔄 從 LocalDB 遷移到 PostgreSQL 14+
  - 完整的資料遷移
  - Schema 正名化
- 🔄 從本地 Redis 遷移到遠端 Redis
  - 集中式 Session 管理
  - 資料庫 1 專用

#### Schema 重新命名
- 🔄 `sysfunction` → `system_functions`
- 🔄 `user_detail` → `users`
- 🔄 `sys_profile` → `sys_profiles`
- 🔄 `func_module_name` → `module_code`

#### 前端升級
- 🔄 React 18 → React 19
- 🔄 改善 Modal 編輯體驗
- 🔄 統一錯誤處理機制

### 移除 (Removed)

- ❌ **編號規則功能** (numbering_rules)
  - 原因: 屬於客製化功能,應依專案需求客製開發
  - 刪除內容:
    - sequence_rules 資料表
    - sequence_values 資料表
    - Backend: Model + Schema + Route (582 行)
    - Frontend: Page + Service (989 行)
  - 詳見: `docs/REMOVE_NUMBERING_RULES_FEATURE.md`

### 修正 (Fixed)

- 🐛 修正個人資料編輯按鈕立即顯示「儲存成功」問題
  - 原因: Token 請求未完成就進入編輯模式
  - 解決: 新增 isRequestingToken 狀態,等待 Token 後再進入編輯
- 🐛 修正 Redis 資料寫入錯誤位置問題
  - 原因: 多個 Backend 進程使用不同 Redis 配置
  - 解決: 統一使用遠端 Redis (10.1.0.20:6379 DB1)
- 🐛 修正用戶端維護 Modal 關閉後資料殘留
  - 解決: 正確清理表單和編輯狀態
- 🐛 修正 TenantUsersPage 新增功能缺少 tenant_type
  - 解決: 新增 tenant_type 欄位到 Schema

### 安全性 (Security)

- 🔒 Schema 設計安全改善
  - Create/Update Schema 不包含 org_id
  - 後端明確指定 org_id,防止使用者偽造
- 🔒 交易令牌機制強化
  - Token 內嵌權限資訊
  - 防止權限繞過攻擊

### 文件 (Documentation)

- 📝 新增核心設計文件
  - org_id 設計說明
  - Schema 設計指導原則
  - 交易令牌使用指南
  - 雙層權限架構說明
- 📝 新增開發指南
  - 功能開發範本
  - 部署指南
  - 命名規範
- 📝 新增完成報告
  - PostgreSQL 遷移完成
  - Token v3.0 完成
  - 系統通知功能完成
  - Schema 重新命名完成

## 開發里程碑

### Phase 1: 基礎建設 (2026-01-18 ~ 2026-01-20)
- ✅ 資料庫架構設計
- ✅ Backend API 框架建立
- ✅ Frontend 專案初始化
- ✅ 基本認證機制

### Phase 2: 核心功能 (2026-01-21 ~ 2026-01-25)
- ✅ 權限系統實作
- ✅ 組織管理功能
- ✅ 使用者管理功能
- ✅ 系統設定功能

### Phase 3: 進階功能 (2026-01-26 ~ 2026-01-28)
- ✅ 系統通知功能
- ✅ 多語系支援
- ✅ 檔案附件管理
- ✅ 交易令牌優化

### Phase 4: 整合與優化 (2026-01-28 ~ 2026-01-29)
- ✅ PostgreSQL 遷移
- ✅ Redis 集中管理
- ✅ 錯誤處理改善
- ✅ 非基底功能清理

### Phase 5: 封裝與文件 (2026-01-29)
- ✅ 文件整理
- ✅ 部署指南
- ✅ README 撰寫
- ✅ 版本記錄

## 技術債務

無重大技術債務。

## 已知問題

無重大已知問題。

## 未來規劃

### v1.1.0 (規劃中)
- [ ] 報表功能
- [ ] 資料匯入/匯出
- [ ] 進階搜尋功能
- [ ] 批次操作

### v1.2.0 (規劃中)
- [ ] API 版本控制
- [ ] Webhook 支援
- [ ] 第三方整合

---

**日誌維護者**: Claude Code
**最後更新**: 2026-01-29
