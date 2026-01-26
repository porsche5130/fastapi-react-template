"""
Transaction Token Routes
交易令牌相關路由 - 功能級別的一次性令牌

設計理念:
- 每個功能(func_code)申請一個 token
- Token 綁定功能,功能綁定使用者權限
- Token 有效期 15 分鐘,一次性使用(或可設為多次使用)
- 進入功能頁面時申請,操作完成或離開頁面時銷毀
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import check_permission
from app.core.redis_client import get_redis
from app.models.user import User

# 先初始化 logger
logger = logging.getLogger(__name__)
router = APIRouter()

# 優先使用 Redis 版本,如果 Redis 不可用則使用記憶體版本
try:
    from app.core.transaction_token_redis import (
        generate_txn_token,
        verify_txn_token,
        revoke_txn_token,
        get_token_info
    )
    logger.info("✅ 使用 Redis 儲存交易令牌")
except Exception:
    from app.core.transaction_token import (
        generate_txn_token,
        verify_txn_token,
        revoke_txn_token,
        get_token_info
    )
    logger.warning("⚠️  使用記憶體儲存交易令牌")


class TokenRequest(BaseModel):
    """Token 申請請求"""
    func_code: str  # 功能代碼 (如: role_rights, organizations, users)


class TokenResponse(BaseModel):
    """Token 回應"""
    txn_token: str
    expires_in: int  # 秒數
    func_code: str
    permissions: dict  # 使用者在此功能的權限


@router.post("/request", response_model=TokenResponse, summary="申請功能交易令牌")
async def request_transaction_token(
    request: TokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    申請功能交易令牌（自動管理機制）

    使用者進入某個功能頁面時,申請該功能的交易令牌。
    - 如果該 session + function 已有有效 token,自動延長到 30 分鐘
    - 如果沒有或已過期,建立新的 token,有效期 30 分鐘

    Token 綁定 session_id + system_functions_id,功能綁定使用者權限。

    - **func_code**: 功能代碼

    需要提供 Bearer Token (session_id)

    Example:
        使用者進入「角色權限設定」頁面:
        1. 前端呼叫:
           POST /api/transaction/request
           {
               "func_code": "role_rights"
           }

        2. 後端回應:
           {
               "txn_token": "abc123...",
               "expires_in": 1800,
               "func_code": "role_rights",
               "permissions": {
                   "create": false,
                   "read": true,
                   "update": false,
                   "delete": false,
                   "print": false,
                   "file": false
               }
           }

        3. 前端根據 permissions 決定 UI 元件的啟用/停用
        4. 所有操作都帶著這個 txn_token
    """
    func_code = request.func_code

    # 取得 session_id
    session_id = getattr(current_user, 'current_session_id', None)
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無法取得 Session ID,請重新登入"
        )

    # 檢查使用者是否有該功能的任何權限
    permissions = {
        "create": check_permission(db, current_user, func_code, "create"),
        "read": check_permission(db, current_user, func_code, "read"),
        "update": check_permission(db, current_user, func_code, "update"),
        "delete": check_permission(db, current_user, func_code, "delete"),
        "print": check_permission(db, current_user, func_code, "print"),
        "file": check_permission(db, current_user, func_code, "file")
    }

    # 檢查是否有任何權限
    has_any_permission = any(permissions.values())

    if not has_any_permission:
        logger.warning(
            f"[Transaction Token] 使用者 {current_user.id} 嘗試申請無權限的功能令牌: {func_code}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"無權限使用功能: {func_code}"
        )

    # 取得 system_function_id
    from app.models.system_functions import SystemFunction
    system_function = db.query(SystemFunction).filter(
        SystemFunction.func_code == func_code
    ).first()

    if not system_function:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"系統功能不存在: {func_code}"
        )

    # 使用新的自動管理機制: 取得或建立 Token（自動延長）
    from app.core.transaction_token_redis import get_or_create_function_token

    txn_token = get_or_create_function_token(
        session_id=session_id,
        system_functions_id=system_function.id,
        valid_minutes=30  # 改為 30 分鐘
    )

    if not txn_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="無法建立交易令牌,請稍後再試"
        )

    logger.info(
        f"[Transaction Token] 使用者 {current_user.id} ({current_user.username}) "
        f"取得功能 {func_code} (ID: {system_function.id}) 的交易令牌,權限: {permissions}"
    )

    return TokenResponse(
        txn_token=txn_token,
        expires_in=30 * 60,  # 30 分鐘 = 1800 秒
        func_code=func_code,
        permissions=permissions
    )


@router.get("/info", summary="查詢令牌資訊")
async def get_transaction_token_info(
    x_txn_token: str = Header(..., alias="X-Txn-Token"),
    current_user: User = Depends(get_current_user)
):
    """
    查詢交易令牌資訊

    前端可以用此 API 檢查 token 是否仍然有效,以及剩餘時間。

    需要提供 Bearer Token (session_id) 和 X-Txn-Token Header
    """
    token_info = get_token_info(x_txn_token)

    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易令牌不存在或已過期"
        )

    # 驗證 token 是否屬於當前 session
    session_id = getattr(current_user, 'current_session_id', None)
    if token_info["session_id"] != session_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="交易令牌與 Session 不符"
        )

    return {
        "func_code": token_info["func_code"],
        "remaining_seconds": token_info["remaining_seconds"],
        "used": token_info["used"]
    }


@router.post("/revoke", summary="撤銷交易令牌")
async def revoke_transaction_token(
    x_txn_token: str = Header(..., alias="X-Txn-Token"),
    current_user: User = Depends(get_current_user)
):
    """
    撤銷交易令牌

    使用者離開功能頁面時,主動撤銷令牌。

    需要提供 Bearer Token (session_id) 和 X-Txn-Token Header
    """
    # 先檢查 token 是否屬於當前 session
    token_info = get_token_info(x_txn_token)
    session_id = getattr(current_user, 'current_session_id', None)
    if token_info and token_info["session_id"] != session_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="交易令牌與 Session 不符"
        )

    success = revoke_txn_token(x_txn_token)

    if success:
        logger.info(
            f"[Transaction Token] 使用者 {current_user.id} ({current_user.username}) "
            f"撤銷交易令牌"
        )
        return {"message": "交易令牌已撤銷"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易令牌不存在"
        )


# ============ 用於其他 API 的依賴項 ============

def require_txn_token(
    func_code: str,
    required_permission: str = None,
    one_time_use: bool = False
):
    """
    交易令牌驗證依賴項

    用於需要 txn_token 驗證的 API 端點。

    Args:
        func_code: 功能代碼
        required_permission: 必要的權限類型 (create/read/update/delete/print/file)
                            如果為 None,只驗證 token 有效性
        one_time_use: 是否為一次性使用 (預設 False,因為同一功能內可多次操作)

    Example:
        @router.post("/role_rights/save")
        async def save_role_rights(
            data: DataModel,
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_txn_token("role_rights", "update"))
        ):
            # Token 已驗證,且使用者有 update 權限
            ...
    """
    async def dependency(
        x_txn_token: str = Header(..., alias="X-Txn-Token"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # 取得 session_id
        session_id = getattr(current_user, 'current_session_id', None)
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無法取得 Session ID,請重新登入"
            )

        # 驗證 token (綁定 session_id)
        verify_txn_token(
            txn_token=x_txn_token,
            session_id=session_id,
            func_code=func_code,
            one_time_use=one_time_use
        )

        # 如果指定了必要權限,額外檢查
        if required_permission:
            has_permission = check_permission(db, current_user, func_code, required_permission)
            if not has_permission:
                logger.warning(
                    f"[Transaction Token] 使用者 {current_user.id} Token 有效但缺少權限: "
                    f"{func_code}.{required_permission}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"無權限執行操作: {func_code}.{required_permission}"
                )

        logger.info(
            f"[Transaction Token] 使用者 {current_user.id} 使用令牌執行: "
            f"{func_code}" + (f".{required_permission}" if required_permission else "")
        )
        return None

    return dependency
