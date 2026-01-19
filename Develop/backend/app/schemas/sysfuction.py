"""
System Function Schemas
系統功能明細檔 API Schema
"""

from typing import Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field


class SysFunctionBase(BaseModel):
    """系統功能基本資料"""
    func_code: str = Field(..., max_length=200, description="功能代碼")
    upper_func_id: int = Field(0, description="上層功能ID (0表示根節點)")
    func_cname: str = Field(..., max_length=200, description="功能中文名稱")
    func_ename: str = Field(..., max_length=200, description="功能英文名稱")
    func_type: int = Field(..., description="功能類型 (1:節點, 2:功能)")
    func_order: int = Field(..., description="排序順序")
    func_icon: Optional[str] = Field(None, max_length=200, description="圖示")
    func_module_name: Optional[str] = Field(None, max_length=200, description="模組名稱/路徑")
    module_item: List[str] = Field(default_factory=list, description="可設定權限 (Create/Read/Update/Delete/Print/File)")
    description: Optional[str] = Field(None, description="功能說明")
    is_mana: bool = Field(False, description="是否為管理功能")
    is_active: bool = Field(True, description="是否啟用")


class SysFunctionCreate(SysFunctionBase):
    """建立系統功能"""
    pass


class SysFunctionUpdate(BaseModel):
    """更新系統功能（所有欄位可選）"""
    func_code: Optional[str] = Field(None, max_length=200, description="功能代碼")
    upper_func_id: Optional[int] = Field(None, description="上層功能ID")
    func_cname: Optional[str] = Field(None, max_length=200, description="功能中文名稱")
    func_ename: Optional[str] = Field(None, max_length=200, description="功能英文名稱")
    func_type: Optional[int] = Field(None, description="功能類型")
    func_order: Optional[int] = Field(None, description="排序順序")
    func_icon: Optional[str] = Field(None, max_length=200, description="圖示")
    func_module_name: Optional[str] = Field(None, max_length=200, description="模組名稱/路徑")
    module_item: Optional[List[str]] = Field(None, description="可設定權限 (Create/Read/Update/Delete/Print/File)")
    description: Optional[str] = Field(None, description="功能說明")
    is_mana: Optional[bool] = Field(None, description="是否為管理功能")
    is_active: Optional[bool] = Field(None, description="是否啟用")


class SysFunctionResponse(SysFunctionBase):
    """系統功能回應資料"""
    id: int
    edit_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
