"""
Authentication Routes
認證相關路由
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.user_detail import UserDetail
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserProfile

router = APIRouter()


@router.post("/login", response_model=Token, summary="使用者登入")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    使用者登入

    - **account**: 登入帳號
    - **password**: 密碼

    回傳 JWT Token
    """
    # 查詢使用者
    user = db.query(UserDetail).filter(UserDetail.account == login_data.account).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤"
        )

    # 驗證密碼
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤"
        )

    # 檢查帳號是否啟用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="帳號已停用"
        )

    # 更新最後登入時間與 IP
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = request.client.host if request.client else None
    db.commit()

    # 建立 JWT Token (sub 必須是字串)
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserProfile, summary="取得當前使用者資訊")
async def get_current_user_profile(
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得當前登入使用者的個人資料

    需要提供 Bearer Token
    """
    return current_user


@router.post("/logout", summary="使用者登出")
async def logout(
    current_user: UserDetail = Depends(get_current_user)
):
    """
    使用者登出

    需要提供 Bearer Token
    （前端應清除儲存的 Token）
    """
    return {"message": "登出成功"}
