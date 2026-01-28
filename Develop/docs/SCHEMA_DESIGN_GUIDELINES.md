# Schema 設計指導原則

## 問題背景

在開發過程中發現多個 API 存在 **Schema 設計不當** 的問題:

1. **編號規則 (numbering_rule)**: Create Schema 包含 `org_id`,導致與後端明確指定的 `org_id` 參數衝突
2. **系統設定 (sys_profile)**: Update Schema 包含 `sys_organization`,但這是共用的全局設定,不應該讓使用者隨意修改

## 核心原則

### 原則 1: Create/Update Schema 不應包含後端自動填入的欄位

**不應該在 Schema 中包含的欄位**:
- `org_id`: 應該從 `current_user.organization_id` 取得
- `created_by`: 應該從 `current_user.id` 取得
- `updated_by`: 應該從 `current_user.id` 取得
- `created_at`: 應該由資料庫自動產生
- `updated_at`: 應該由資料庫自動產生
- `edit_by`: 應該從 `current_user.id` 取得

**原因**:
1. **安全性**: 防止使用者偽造組織 ID 或使用者 ID
2. **一致性**: 確保這些欄位由系統統一管理
3. **避免衝突**: 防止 Schema 欄位與後端明確指定的參數衝突

### 原則 2: 區分不同用途的 Schema

為不同的操作建立專用的 Schema:

```python
# 基本資料 (共用欄位)
class ResourceBase(BaseModel):
    name: str
    description: Optional[str] = None

# 建立請求 (只包含使用者可輸入的欄位)
class ResourceCreate(ResourceBase):
    # 不包含 org_id, created_by 等
    pass

# 更新請求 (只包含使用者可修改的欄位)
class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    # 不包含 org_id, updated_by 等

# 回應資料 (包含所有欄位)
class ResourceResponse(ResourceBase):
    id: int
    org_id: int  # 可以在回應中包含
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
```

### 原則 3: 後端路由正確處理自動欄位

```python
@router.post("/", response_model=ResourceResponse)
async def create_resource(
    data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("resource", "create"))
):
    try:
        # 正確: 不展開包含 org_id 的欄位
        resource_dict = data.model_dump()

        new_resource = Resource(
            **resource_dict,
            org_id=current_user.organization_id,  # 後端明確指定
            created_by=current_user.id             # 後端明確指定
        )

        db.add(new_resource)
        db.commit()
        db.refresh(new_resource)

        return new_resource
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "RESOURCE_CREATE_FAILED",
                "message": f"建立資源失敗: {str(e)}",
                "details": str(e)
            }
        )

@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("resource", "update"))
):
    resource = db.query(Resource).filter(
        and_(
            Resource.id == resource_id,
            Resource.org_id == current_user.organization_id
        )
    ).first()

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="資源不存在"
        )

    try:
        # 更新使用者可修改的欄位
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(resource, field, value)

        # 後端明確更新系統欄位
        resource.updated_by = current_user.id
        resource.updated_at = func.now()

        db.commit()
        db.refresh(resource)

        return resource
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "RESOURCE_UPDATE_FAILED",
                "message": f"更新資源失敗: {str(e)}",
                "details": str(e)
            }
        )
```

## 實際案例修正

### 案例 1: 編號規則 (已修正)

#### 問題程式碼

```python
# schemas/numberingrule.py
class SequenceRuleCreate(SequenceRuleBase):
    org_id: Optional[int] = Field(1, description="組織ID")  # ❌ 不應該在這裡

# routes/numberingrule.py
new_rule = SequenceRule(
    **rule_data.model_dump(),              # ❌ 包含 org_id=1
    org_id=current_user.organization_id,   # ❌ 再次指定 org_id
    created_by=current_user.id
)
# 結果: TypeError: got multiple values for keyword argument 'org_id'
```

#### 修正後程式碼

**方案 1: 從 Schema 移除 org_id (理想)**

```python
# schemas/numberingrule.py
class SequenceRuleCreate(SequenceRuleBase):
    # ✅ 移除 org_id
    pass

# routes/numberingrule.py
new_rule = SequenceRule(
    **rule_data.model_dump(),
    org_id=current_user.organization_id,  # ✅ 只有這裡指定
    created_by=current_user.id
)
```

**方案 2: 展開時排除 org_id (目前採用)**

```python
# schemas/numberingrule.py (保持不變)
class SequenceRuleCreate(SequenceRuleBase):
    org_id: Optional[int] = Field(1, description="組織ID")

# routes/numberingrule.py
rule_dict = rule_data.model_dump(exclude={'org_id'})  # ✅ 明確排除
new_rule = SequenceRule(
    **rule_dict,
    org_id=current_user.organization_id,  # ✅ 明確指定
    created_by=current_user.id
)
```

### 案例 2: 系統設定 (需要修正)

#### 問題分析

```python
# models/sysprofile.py
class SysProfile(Base):
    id = Column(Integer, primary_key=True, default=1)  # 固定為 1
    sys_organization = Column(Integer, ForeignKey("organizations.id"), nullable=False, default=1)

    __table_args__ = (
        CheckConstraint("id = 1", name="chk_sys_profile_id"),  # 只能有一筆
    )
```

**問題**:
- `sys_organization` 是指「管理此系統的組織」
- 這是**全局唯一的系統設定**,不應該讓一般使用者隨意修改
- 目前的 Update Schema 包含 `sys_organization`,存在安全風險

#### 修正方案

**選項 A: 從 Update Schema 移除 (推薦)**

如果只有系統管理員可以修改管理組織:

```python
# schemas/sysprofile.py
class SysProfileUpdate(BaseModel):
    is_service: Optional[bool] = None
    sys_url: Optional[str] = None
    sys_ctitle: Optional[str] = None
    sys_etitle: Optional[str] = None
    sys_ccopyright: Optional[str] = None
    sys_ecopyright: Optional[str] = None
    # ❌ 移除 sys_organization
    sys_mana_email: Optional[str] = None

# routes/sysprofile.py (保持不變)
# 只有明確包含在 Update Schema 中的欄位可以被更新
```

**選項 B: 權限檢查**

如果需要某些使用者可以修改:

```python
# routes/sysprofile.py
@router.put("/", response_model=SysProfileResponse)
async def update_sys_profile(
    profile_data: SysProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _token: None = Depends(require_txn_token("sys_profile", "update"))
):
    profile = db.query(SysProfile).filter(SysProfile.id == 1).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="系統設定不存在"
        )

    # 更新欄位
    update_data = profile_data.model_dump(exclude_unset=True)

    # ✅ 檢查是否嘗試修改 sys_organization
    if 'sys_organization' in update_data:
        # 檢查使用者是否為系統管理員
        if not current_user.is_system_admin:  # 假設有這個欄位
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有系統管理員可以修改管理組織"
            )

    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.edit_by = current_user.id
    profile.updated_at = func.now()

    db.commit()
    db.refresh(profile)

    return profile
```

## 檢查清單

在建立或修改 API 時,請檢查:

### Schema 設計
- [ ] Create Schema 是否包含 `org_id`? → **應該移除**
- [ ] Create Schema 是否包含 `created_by`? → **應該移除**
- [ ] Update Schema 是否包含 `updated_by`? → **應該移除**
- [ ] Update Schema 是否包含 `org_id`? → **應該移除**
- [ ] Schema 是否包含系統自動產生的欄位? → **應該移除**

### 路由處理
- [ ] Create 路由是否明確指定 `org_id=current_user.organization_id`?
- [ ] Create 路由是否明確指定 `created_by=current_user.id`?
- [ ] Update 路由是否明確指定 `updated_by=current_user.id`?
- [ ] 是否有 try-catch 錯誤處理?
- [ ] 錯誤訊息是否結構化 (包含 error_code, message, details)?

### 安全性
- [ ] 使用者是否可以偽造 `org_id`? → **應該防止**
- [ ] 使用者是否可以偽造 `created_by`? → **應該防止**
- [ ] 查詢資料時是否過濾 `org_id`? → **應該過濾**
- [ ] 是否有適當的權限檢查?

## 需要檢查的 API 清單

### 已修正
- ✅ 編號規則 (numbering_rules) - 已修正 create 路由

### 待檢查
- ⬜ 系統設定 (sys_profile) - 需要檢查 `sys_organization` 欄位
- ⬜ 組織管理 (organizations)
- ⬜ 使用者管理 (users)
- ⬜ 角色管理 (user_roles)
- ⬜ 系統功能 (system_functions)
- ⬜ 用戶端維護 (tenant_users)

## 修正步驟模板

### 步驟 1: 檢查 Model

```python
# app/models/resource.py
class Resource(Base):
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    # ... 其他欄位
```

### 步驟 2: 修正 Schema

```python
# app/schemas/resource.py
class ResourceBase(BaseModel):
    name: str
    # 只包含業務欄位

class ResourceCreate(ResourceBase):
    # ❌ 不要包含 org_id, created_by
    pass

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    # ❌ 不要包含 org_id, updated_by
```

### 步驟 3: 修正路由

```python
# app/routes/resource.py
@router.post("/")
async def create_resource(
    data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        new_resource = Resource(
            **data.model_dump(),
            org_id=current_user.organization_id,  # ✅ 後端指定
            created_by=current_user.id             # ✅ 後端指定
        )
        db.add(new_resource)
        db.commit()
        db.refresh(new_resource)
        return new_resource
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "RESOURCE_CREATE_FAILED",
                "message": f"建立失敗: {str(e)}",
                "details": str(e)
            }
        )
```

## 參考資料

- [FIX_NUMBERING_RULE_CREATE_ISSUE.md](./FIX_NUMBERING_RULE_CREATE_ISSUE.md) - 編號規則修正案例
- [ERROR_HANDLING_IMPROVEMENT.md](./ERROR_HANDLING_IMPROVEMENT.md) - 錯誤處理改善

## 修正日期

- **建立日期**: 2026-01-28
- **建立者**: Claude Code
- **版本**: v1.0.0
