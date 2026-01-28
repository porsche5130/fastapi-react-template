# org_id 設計說明

## 概念

`org_id` (組織ID) 是多租戶系統 (Multi-tenancy) 的核心欄位,用於實現資料隔離。

## 系統中的組織欄位

### 1. 使用 `organization_id` 的表

#### users (使用者表)
```python
# app/models/user.py:22
organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
```

**說明**:
- 使用者**屬於**某個組織
- 使用者登入後,`current_user.organization_id` 代表其所屬組織
- 所有 API 都使用這個值來過濾資料

### 2. 使用 `org_id` 的表

#### sequence_rules (編號規則表)
```python
# app/models/numberingrule.py:45
org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, default=1, comment="組織ID")
```

**說明**:
- 每個組織有自己的編號規則
- 不同組織可以有相同的 `rule_code`
- 唯一約束: `(rule_code, org_id)`

#### sequence_values (編號流水號表)
```python
# app/models/numberingrule.py:93
org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, default=1, comment="組織ID")
```

**說明**:
- 儲存每個組織的流水號當前值
- 與編號規則關聯
- 確保不同組織的流水號互不干擾

#### file_attachments (檔案附件表)
```python
# app/models/fileattachment.py:73
org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, default=1, comment="組織ID")
```

**說明**:
- 檔案附件屬於某個組織
- 不同組織的檔案完全隔離

## 資料隔離機制

### 查詢時的過濾

```python
# 正確的查詢方式 - 總是過濾 org_id
rules = db.query(SequenceRule).filter(
    and_(
        SequenceRule.org_id == current_user.organization_id,
        SequenceRule.is_active == True
    )
).all()
```

### 建立時的自動填入

```python
# 正確的建立方式 - 後端強制指定 org_id
rule_dict = rule_data.model_dump(exclude={'org_id'})
new_rule = SequenceRule(
    **rule_dict,
    org_id=current_user.organization_id,  # 從登入使用者取得
    created_by=current_user.id
)
```

### 更新時的驗證

```python
# 正確的更新方式 - 驗證資料屬於使用者的組織
rule = db.query(SequenceRule).filter(
    and_(
        SequenceRule.id == rule_id,
        SequenceRule.org_id == current_user.organization_id  # 安全檢查
    )
).first()

if not rule:
    raise HTTPException(status_code=404, detail="資料不存在或無權限")
```

### 刪除時的驗證

```python
# 正確的刪除方式 - 驗證資料屬於使用者的組織
rule = db.query(SequenceRule).filter(
    and_(
        SequenceRule.id == rule_id,
        SequenceRule.org_id == current_user.organization_id  # 安全檢查
    )
).first()

if not rule:
    raise HTTPException(status_code=404, detail="資料不存在或無權限")

db.delete(rule)
```

## 為什麼不在 Schema 中包含 org_id?

### 安全性問題

```python
# ❌ 危險!使用者可以偽造 org_id
class SequenceRuleCreate(BaseModel):
    rule_code: str
    org_id: int = 1  # 使用者可以傳 org_id=999

# 前端送: { rule_code: "TEST", org_id: 999 }
new_rule = SequenceRule(**rule_data.model_dump())
# 結果: 建立了屬於組織 999 的資料!
```

### 正確做法

```python
# ✅ 安全!Schema 不包含 org_id
class SequenceRuleCreate(BaseModel):
    rule_code: str
    # 不包含 org_id

# 後端強制使用登入使用者的組織
rule_dict = rule_data.model_dump()
new_rule = SequenceRule(
    **rule_dict,
    org_id=current_user.organization_id  # 後端決定
)
```

## 實際範例

### 範例 1: 多組織使用相同規則代碼

```
資料庫內容:

id | rule_code | rule_name | org_id | 說明
---|-----------|-----------|--------|-------------------
1  | PO        | 採購單號  | 1      | 匠耘公司的採購單號
2  | PO        | 採購單號  | 2      | ABC公司的採購單號
3  | INV       | 發票編號  | 1      | 匠耘公司的發票編號
4  | SO        | 銷貨單號  | 2      | ABC公司的銷貨單號
```

**查詢結果**:

```python
# 匠耘公司使用者 (org_id=1) 查詢
current_user.organization_id = 1
rules = query.filter(SequenceRule.org_id == 1).all()
# 結果: [PO, INV]

# ABC公司使用者 (org_id=2) 查詢
current_user.organization_id = 2
rules = query.filter(SequenceRule.org_id == 2).all()
# 結果: [PO, SO]
```

### 範例 2: 防止跨組織存取

```python
# 匠耘公司使用者 (org_id=1) 嘗試存取 ABC公司的資料
current_user.organization_id = 1

rule = db.query(SequenceRule).filter(
    and_(
        SequenceRule.id == 4,  # ABC公司的 SO 規則
        SequenceRule.org_id == current_user.organization_id  # org_id=1
    )
).first()

# 結果: None (找不到,因為 org_id 不符合)
```

## 全局共用資料 (不需要 org_id)

某些資料是**全系統共用**的,不需要 org_id:

### sys_profiles (系統設定)
```python
# 全系統只有一筆,id=1
class SysProfile(Base):
    __tablename__ = "sys_profiles"
    id = Column(Integer, primary_key=True, default=1)
    sys_organization = Column(Integer, ForeignKey("organizations.id"))  # 管理此系統的組織

    __table_args__ = (
        CheckConstraint("id = 1", name="chk_sys_profile_id"),
    )
```

**說明**:
- `sys_organization` 不是資料隔離用的
- 而是記錄「哪個組織管理這個系統」
- 所有組織共用這筆系統設定

### system_functions (系統功能)
```python
# 全系統共用的功能選單
class SystemFunction(Base):
    __tablename__ = "system_functions"
    id = Column(Integer, primary_key=True)
    func_code = Column(String(50))
    # 沒有 org_id,所有組織共用
```

### organizations (組織表)
```python
# 組織本身當然不需要 org_id
class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)  # 這就是 org_id
    name = Column(String(200))
```

## 設計原則總結

### 需要 org_id 的表
業務資料表,每個組織有自己的資料:
- ✅ sequence_rules (編號規則)
- ✅ sequence_values (流水號)
- ✅ file_attachments (檔案附件)
- ✅ tenant_users (用戶端資料) - 如果有的話
- ✅ projects (專案) - 如果有的話
- ✅ transactions (交易記錄) - 如果有的話

### 不需要 org_id 的表
系統級或參考資料表:
- ❌ sys_profiles (系統設定,全局共用)
- ❌ system_functions (系統功能選單,全局共用)
- ❌ organizations (組織表本身)
- ❌ user_roles (角色定義,可能全局共用)

### users 表的特殊情況
```python
# users 表使用 organization_id (不是 org_id)
organization_id = Column(Integer, ForeignKey("organizations.id"))
```

**原因**:
- 使用者**屬於**某個組織
- 但使用者表本身不是業務資料
- 使用更明確的名稱 `organization_id`

## 檢查清單

在設計新表時,問自己:

1. **這是業務資料嗎?**
   - 是 → 需要 org_id
   - 否 → 可能不需要

2. **不同組織需要獨立的資料嗎?**
   - 是 → 需要 org_id
   - 否 → 不需要

3. **這是全系統共用的設定或參考資料嗎?**
   - 是 → 不需要 org_id
   - 否 → 需要 org_id

4. **如果沒有 org_id,會有安全問題嗎?**
   - 是 → 必須有 org_id
   - 否 → 可能不需要

## 修正日期

- **建立日期**: 2026-01-28
- **建立者**: Claude Code
- **版本**: v1.0.0
