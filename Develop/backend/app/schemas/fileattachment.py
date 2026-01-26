"""
File Attachments Schema
檔案附件管理 Schema
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# ============ 檔案附件 Schema ============

class FileAttachmentBase(BaseModel):
    """檔案附件基礎 Schema"""
    category: str = Field(..., description="檔案分類")
    business_type: Optional[str] = Field(None, max_length=50, description="業務類型")
    related_table: Optional[str] = Field(None, max_length=100, description="關聯資料表")
    related_id: Optional[int] = Field(None, description="關聯記錄 ID")

    access_level: str = Field("private", description="存取等級")
    is_public: bool = Field(False, description="是否公開")
    allowed_roles: Optional[List[str]] = Field(None, description="允許存取的角色")
    allowed_users: Optional[List[int]] = Field(None, description="允許存取的使用者 ID")

    description: Optional[str] = Field(None, description="檔案說明")
    tags: Optional[List[str]] = Field(None, description="標籤")
    expires_at: Optional[datetime] = Field(None, description="過期時間")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = ["image", "document", "archive", "video", "audio", "other"]
        if v not in allowed:
            raise ValueError(f"category must be one of: {', '.join(allowed)}")
        return v

    @field_validator("access_level")
    @classmethod
    def validate_access_level(cls, v: str) -> str:
        if v not in ["public", "private", "restricted"]:
            raise ValueError("access_level must be one of: public, private, restricted")
        return v


class FileAttachmentCreate(FileAttachmentBase):
    """建立檔案附件 Schema (由後端自動填入檔案資訊)"""
    org_id: Optional[int] = Field(1, description="組織ID")


class FileAttachmentUpdate(BaseModel):
    """更新檔案附件 Schema"""
    description: Optional[str] = Field(None, description="檔案說明")
    tags: Optional[List[str]] = Field(None, description="標籤")

    access_level: Optional[str] = Field(None, description="存取等級")
    is_public: Optional[bool] = Field(None, description="是否公開")
    allowed_roles: Optional[List[str]] = Field(None, description="允許存取的角色")
    allowed_users: Optional[List[int]] = Field(None, description="允許存取的使用者 ID")

    expires_at: Optional[datetime] = Field(None, description="過期時間")

    @field_validator("access_level")
    @classmethod
    def validate_access_level(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ["public", "private", "restricted"]:
            raise ValueError("access_level must be one of: public, private, restricted")
        return v


class FileAttachmentResponse(BaseModel):
    """檔案附件回應 Schema"""
    id: int
    original_name: str
    storage_path: str
    file_size: int
    mime_type: str
    file_hash: str

    category: str
    business_type: Optional[str]
    related_table: Optional[str]
    related_id: Optional[int]

    access_level: str
    is_public: bool
    allowed_roles: Optional[List[str]]
    allowed_users: Optional[List[int]]

    is_temp: bool
    confirmed_at: Optional[datetime]
    download_count: int
    last_downloaded_at: Optional[datetime]

    version: int
    previous_version_id: Optional[int]

    thumbnail_path: Optional[str]
    file_metadata: Optional[Dict[str, Any]]
    description: Optional[str]
    tags: Optional[List[str]]

    expires_at: Optional[datetime]

    org_id: int
    uploaded_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    # 額外欄位 (前端用)
    download_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    class Config:
        from_attributes = True


class FileAttachmentListResponse(BaseModel):
    """檔案附件列表回應 Schema"""
    total: int
    items: List[FileAttachmentResponse]


# ============ 檔案上傳 Schema ============

class FileUploadResponse(BaseModel):
    """檔案上傳回應 Schema"""
    file_id: int = Field(..., description="檔案 ID")
    original_name: str = Field(..., description="原始檔案名稱")
    file_size: int = Field(..., description="檔案大小")
    mime_type: str = Field(..., description="MIME 類型")
    file_hash: str = Field(..., description="檔案雜湊")
    is_duplicate: bool = Field(..., description="是否為重複檔案")
    download_url: str = Field(..., description="下載 URL")
    thumbnail_url: Optional[str] = Field(None, description="縮圖 URL")
    is_temp: bool = Field(..., description="是否為臨時檔案")
    expires_at: Optional[datetime] = Field(None, description="過期時間")


class FileConfirmRequest(BaseModel):
    """檔案確認請求 Schema"""
    file_id: int = Field(..., description="檔案 ID")


class FileConfirmResponse(BaseModel):
    """檔案確認回應 Schema"""
    message: str = Field(..., description="訊息")
    file_id: int = Field(..., description="檔案 ID")
    confirmed_at: datetime = Field(..., description="確認時間")


# ============ 檔案查詢 Schema ============

class FileQueryParams(BaseModel):
    """檔案查詢參數 Schema"""
    category: Optional[str] = Field(None, description="檔案分類")
    business_type: Optional[str] = Field(None, description="業務類型")
    related_table: Optional[str] = Field(None, description="關聯資料表")
    related_id: Optional[int] = Field(None, description="關聯記錄 ID")
    is_temp: Optional[bool] = Field(None, description="是否為臨時檔案")
    uploaded_by: Optional[int] = Field(None, description="上傳者 ID")
    skip: int = Field(0, ge=0, description="跳過筆數")
    limit: int = Field(20, ge=1, le=100, description="每頁筆數")
