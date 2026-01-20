"""
Authentication Schemas
認證相關的 Pydantic Schema
"""

from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """登入請求"""

    account: EmailStr = Field(..., description="登入帳號 (電子郵件)")
    password: str = Field(..., description="密碼")

    class Config:
        json_schema_extra = {
            "example": {
                "account": "porsche@lab.taipei",
                "password": "Aa123456"
            }
        }


class Token(BaseModel):
    """Token 回應"""

    access_token: str = Field(..., description="存取 Token")
    token_type: str = Field(default="bearer", description="Token 類型")


class TokenData(BaseModel):
    """Token 內容"""

    user_id: int = Field(..., description="使用者 ID")
