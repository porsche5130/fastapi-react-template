"""
User Detail Schemas
使用者明細檔 API Schema
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserDetailBase(BaseModel):
    """使用者基本資料"""
    organization_id: int = Field(..., description="組織單位ID")
    account: str = Field(..., max_length=100, description="帳號")
    username: str = Field(..., max_length=200, description="使用者名稱")
    department: Optional[str] = Field(None, max_length=200, description="部門")
    job_title: Optional[str] = Field(None, max_length=200, description="職稱")
    phone: Optional[str] = Field(None, max_length=200, description="電話")
    user_role: List[int] = Field(default_factory=list, description="角色ID陣列")
    is_active: bool = Field(True, description="是否啟用")


class UserDetailCreate(UserDetailBase):
    """建立使用者"""
    password: str = Field(..., min_length=6, max_length=100, description="密碼")


class UserDetailUpdate(BaseModel):
    """更新使用者（所有欄位可選）"""
    organization_id: Optional[int] = Field(None, description="組織單位ID")
    account: Optional[str] = Field(None, max_length=100, description="帳號")
    username: Optional[str] = Field(None, max_length=200, description="使用者名稱")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="密碼")
    department: Optional[str] = Field(None, max_length=200, description="部門")
    job_title: Optional[str] = Field(None, max_length=200, description="職稱")
    phone: Optional[str] = Field(None, max_length=200, description="電話")
    user_role: Optional[List[int]] = Field(None, description="角色ID陣列")
    is_active: Optional[bool] = Field(None, description="是否啟用")


class UserDetailResponse(BaseModel):
    """使用者回應資料（不包含密碼）"""
    id: int
    organization_id: int
    account: str
    username: str
    department: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    user_role: List[int]
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    is_active: bool
    edit_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """修改密碼"""
    old_password: str = Field(..., min_length=6, description="舊密碼")
    new_password: str = Field(..., min_length=6, description="新密碼")
