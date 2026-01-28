# 從 PA6.4 建立通用範本指南

## 概述

PA6.4 是實際的減碳專案,但可以作為基礎建立通用的企業應用範本。

---

## 建立範本的兩種方式

### 方案 1: 建立新的 GitHub 倉庫 (推薦)

**步驟**:

1. **複製專案到新目錄**

```bash
# 複製整個專案
xcopy W:\P-PA6.4 W:\FastAPI-React-Template /E /I /H

# 或使用 robocopy (更快)
robocopy W:\P-PA6.4 W:\FastAPI-React-Template /E /XD .git node_modules __pycache__ venv
```

2. **清理 PA6.4 特定內容**

```bash
cd W:\FastAPI-React-Template

# 刪除 Git 歷史
rmdir /s /q .git

# 初始化新的 Git 倉庫
git init
```

3. **替換專案識別**

需要替換的字串:
- `PA6.4` → `TEMPLATE` (專案代碼)
- `pa64` → `template` (小寫識別)
- `Paris Agreement Article 6.4` → `FastAPI React Multi-Tenant Template`

4. **建立 GitHub 倉庫**

```bash
# 在 GitHub 上建立新倉庫: fastapi-react-template

# 關聯遠端倉庫
git remote add origin https://github.com/你的帳號/fastapi-react-template.git

# 提交並推送
git add .
git commit -m "Initial commit: Multi-tenant template based on PA6.4"
git push -u origin main
```

---

### 方案 2: 使用 Git 分支

保留 PA6.4 主分支,建立 template 分支:

```bash
cd W:\P-PA6.4

# 建立 template 分支
git checkout -b template

# 替換專案識別 (使用腳本)
# ... 執行替換 ...

# 提交
git add .
git commit -m "Create generic template from PA6.4"

# 推送到 GitHub
git push origin template
```

---

## 需要替換的檔案和內容

### 1. 環境配置

**`Develop/backend/.env.example`**

```bash
# 原本
DATABASE_URL=postgresql://admin:your_password@10.1.0.20:5433/pa64_dev

# 改為
DATABASE_URL=postgresql://admin:your_password@10.1.0.20:5433/template_dev
```

### 2. 資料庫設定

**`Develop/backend/app/core/config.py`**

```python
# 原本
class Settings(BaseSettings):
    PROJECT_NAME: str = "PA6.4 Management System"

# 改為
class Settings(BaseSettings):
    PROJECT_NAME: str = "Multi-Tenant Management System"
```

### 3. 初始化資料

**`Develop/backend/app/core/init_data.py`**

```python
# 原本
init_org = Organization(
    org_id="PA64",
    org_name="PA6.4 減碳專案",
    org_code="PA64",
)

# 改為
init_org = Organization(
    org_id="DEMO",
    org_name="示範組織",
    org_code="DEMO",
)
```

### 4. 前端配置

**`Develop/frontend/src/locales/zh-TW/translation.json`**

```json
{
  "appName": "多租戶管理系統",
  "welcome": "歡迎使用多租戶管理系統"
}
```

### 5. README.md

```markdown
# FastAPI React Multi-Tenant Template

企業級多租戶管理系統範本

## 特色

- 🔐 完整的權限系統 (雙層權限架構)
- 🏢 多租戶架構 (org_id 資料隔離)
- 🔑 交易令牌機制
- 🌍 多語系支援
- 📚 完整文檔

## 基於

本範本基於 PA6.4 (Paris Agreement Article 6.4) 減碳專案開發,
已移除業務特定邏輯,保留核心架構和最佳實踐。
```

---

## 自動化替換腳本

**`scripts/create_template.py`**

```python
#!/usr/bin/env python3
"""
將 PA6.4 專案轉換為通用範本的腳本
"""

import os
import re
from pathlib import Path

# 替換映射
REPLACEMENTS = {
    'PA6.4': 'TEMPLATE',
    'pa64': 'template',
    'PA64': 'TEMPLATE',
    'Paris Agreement Article 6.4': 'FastAPI React Multi-Tenant Template',
    'Paris Agreement Article 6.4 管理系統': '多租戶管理系統',
    'PA6.4 減碳專案': '示範組織',
}

# 需要處理的檔案類型
FILE_EXTENSIONS = ['.py', '.md', '.json', '.ts', '.tsx', '.sql', '.env.example', '.yml', '.yaml']

# 排除的目錄
EXCLUDE_DIRS = {'node_modules', '__pycache__', '.git', 'venv', 'build', 'dist'}

def should_process_file(file_path: Path) -> bool:
    """判斷檔案是否需要處理"""
    if any(excluded in file_path.parts for excluded in EXCLUDE_DIRS):
        return False
    return file_path.suffix in FILE_EXTENSIONS or file_path.name in ['.env.example']

def replace_in_file(file_path: Path):
    """替換檔案內容"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        for old, new in REPLACEMENTS.items():
            content = content.replace(old, new)

        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"✓ 已更新: {file_path}")
    except Exception as e:
        print(f"✗ 錯誤: {file_path} - {e}")

def main():
    """主程式"""
    root_dir = Path(__file__).parent.parent

    print("開始轉換 PA6.4 為通用範本...")
    print(f"根目錄: {root_dir}")
    print()

    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and should_process_file(file_path):
            replace_in_file(file_path)

    print()
    print("✅ 轉換完成!")
    print()
    print("請手動檢查以下項目:")
    print("1. README.md - 更新專案描述")
    print("2. CHANGELOG.md - 重置版本歷史")
    print("3. Develop/backend/app/core/init_data.py - 檢查初始資料")
    print("4. 前端多語系檔案 - 更新應用名稱")

if __name__ == '__main__':
    main()
```

**使用方式**:

```bash
# 1. 先複製專案
xcopy W:\P-PA6.4 W:\FastAPI-React-Template /E /I /H

# 2. 執行轉換腳本
cd W:\FastAPI-React-Template
python scripts/create_template.py

# 3. 手動檢查和調整

# 4. 初始化 Git
git init
git add .
git commit -m "Initial commit: Multi-tenant template"
git remote add origin https://github.com/你的帳號/fastapi-react-template.git
git push -u origin main
```

---

## GitHub 倉庫建議

### 倉庫名稱
- `fastapi-react-multitenancy-template`
- `enterprise-web-app-starter`
- `multi-tenant-admin-template`

### 描述
```
🚀 Enterprise-grade multi-tenant web application template

FastAPI + React + PostgreSQL + Redis
Multi-tenant architecture with complete RBAC system
Based on production-ready PA6.4 project
```

### Topics (標籤)
```
fastapi
react
postgresql
redis
multi-tenant
rbac
typescript
python
admin-template
starter-template
```

### README 結構
```markdown
# FastAPI React Multi-Tenant Template

## Features
- Complete RBAC permission system
- Multi-tenant architecture with data isolation
- Transaction token mechanism
- i18n support
- Comprehensive documentation

## Tech Stack
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: React + TypeScript + Ant Design
- Cache: Redis
- Auth: JWT + Session

## Quick Start
See [NEW_PROJECT_SETUP.md](docs/guides/NEW_PROJECT_SETUP.md)

## Documentation
- [Architecture Design](docs/SIMPLIFIED_ARCHITECTURE_DESIGN.md)
- [Feature Development Guide](docs/guides/FEATURE_DEVELOPMENT_TEMPLATE.md)
- [Deployment Strategy](docs/guides/DEPLOYMENT_STRATEGY.md)

## Based On
This template is based on PA6.4 (Paris Agreement Article 6.4)
carbon reduction management system, with business logic removed
and core architecture preserved.

## License
MIT
```

---

## 維護兩個專案

### PA6.4 (實際專案)
- 倉庫: `pa64-carbon-reduction` (私有)
- 用途: 實際的減碳專案開發
- 包含: 業務邏輯、實際資料

### Template (通用範本)
- 倉庫: `fastapi-react-template` (公開)
- 用途: 作為其他專案的起始範本
- 包含: 架構、框架、最佳實踐

### 同步更新
當 PA6.4 有架構改進時:
```bash
# 在 PA6.4 中
git diff main > architecture-improvements.patch

# 在 Template 中
git apply architecture-improvements.patch
```

---

## 建議的下一步

1. **決定方案**
   - 建議使用方案 1 (建立新倉庫)
   - 保持 PA6.4 和 Template 分離

2. **執行轉換**
   - 複製專案到新目錄
   - 執行自動替換腳本
   - 手動檢查和調整

3. **推送到 GitHub**
   - 建立公開倉庫 (或私有,視需求)
   - 撰寫詳細的 README
   - 添加使用範例

4. **維護**
   - PA6.4 改進 → 同步到 Template
   - Template 保持通用性
   - 持續更新文檔

---

**建立日期**: 2026-01-29
