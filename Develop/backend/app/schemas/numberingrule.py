"""
Sequence Rules Schema
編號規則設定 Schema
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# ============ 編號規則 Schema ============

class SequenceRuleBase(BaseModel):
    """編號規則基礎 Schema"""
    rule_code: str = Field(..., max_length=50, description="規則代碼")
    rule_name: str = Field(..., max_length=200, description="規則名稱")
    description: Optional[str] = Field(None, description="規則說明")

    prefix: Optional[str] = Field(None, max_length=20, description="前置字串")
    date_format: Optional[str] = Field(None, max_length=20, description="日期格式")
    sequence_length: int = Field(6, ge=1, le=20, description="流水號長度")
    suffix: Optional[str] = Field(None, max_length=20, description="後置字串")
    separator: str = Field("-", max_length=5, description="分隔符號")

    reset_mode: str = Field("never", description="重置模式")
    example: Optional[str] = Field(None, max_length=200, description="格式範例")
    is_active: bool = Field(True, description="是否啟用")

    @field_validator("reset_mode")
    @classmethod
    def validate_reset_mode(cls, v: str) -> str:
        if v not in ["never", "yearly", "monthly", "daily"]:
            raise ValueError("reset_mode must be one of: never, yearly, monthly, daily")
        return v

    @field_validator("date_format")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ["YYYY", "YYYYMM", "YYYYMMDD"]:
            raise ValueError("date_format must be one of: YYYY, YYYYMM, YYYYMMDD")
        return v


class SequenceRuleCreate(SequenceRuleBase):
    """建立編號規則 Schema"""
    org_id: Optional[int] = Field(1, description="組織ID")


class SequenceRuleUpdate(BaseModel):
    """更新編號規則 Schema"""
    rule_name: Optional[str] = Field(None, max_length=200, description="規則名稱")
    description: Optional[str] = Field(None, description="規則說明")

    prefix: Optional[str] = Field(None, max_length=20, description="前置字串")
    date_format: Optional[str] = Field(None, max_length=20, description="日期格式")
    sequence_length: Optional[int] = Field(None, ge=1, le=20, description="流水號長度")
    suffix: Optional[str] = Field(None, max_length=20, description="後置字串")
    separator: Optional[str] = Field(None, max_length=5, description="分隔符號")

    reset_mode: Optional[str] = Field(None, description="重置模式")
    example: Optional[str] = Field(None, max_length=200, description="格式範例")
    is_active: Optional[bool] = Field(None, description="是否啟用")

    @field_validator("reset_mode")
    @classmethod
    def validate_reset_mode(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ["never", "yearly", "monthly", "daily"]:
            raise ValueError("reset_mode must be one of: never, yearly, monthly, daily")
        return v

    @field_validator("date_format")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ["YYYY", "YYYYMM", "YYYYMMDD"]:
            raise ValueError("date_format must be one of: YYYY, YYYYMM, YYYYMMDD")
        return v


class SequenceRuleResponse(SequenceRuleBase):
    """編號規則回應 Schema"""
    id: int
    org_id: int
    created_by: int
    updated_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SequenceRuleListResponse(BaseModel):
    """編號規則列表回應 Schema"""
    total: int
    items: List[SequenceRuleResponse]


# ============ 編號規則當前值 Schema ============

class SequenceValueResponse(BaseModel):
    """編號規則當前值回應 Schema"""
    id: int
    rule_id: int
    period: str
    current_value: int
    last_generated_at: Optional[datetime]
    org_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============ 編號產生 Schema ============

class GenerateNumberRequest(BaseModel):
    """產生編號請求 Schema"""
    rule_code: str = Field(..., description="規則代碼")
    custom_date: Optional[str] = Field(None, description="自訂日期 (YYYY-MM-DD)")


class GenerateNumberResponse(BaseModel):
    """產生編號回應 Schema"""
    number: str = Field(..., description="產生的編號")
    rule_code: str = Field(..., description="規則代碼")
    sequence_value: int = Field(..., description="流水號")
    period: str = Field(..., description="期間")
    generated_at: datetime = Field(..., description="產生時間")
