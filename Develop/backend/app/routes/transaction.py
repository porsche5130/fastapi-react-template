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

# v3.0: 使用 Redis 版本的交易令牌 (一個 session 一個 token 包含所有權限)
from app.core.transaction_token_redis import (
    verify_txn_token,
    revoke_txn_token,
    get_token_info
)
logger.info("✅ 使用 Redis v3.0 交易令牌 (一個 session 一個 token)")


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
    from app.models.systemfunction import SystemFunction
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
        func_code=system_function.func_code,
        module_code=system_function.module_code,
        permissions=permissions,  # 儲存權限資訊到 token
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


@router.post("/refresh", summary="刷新交易令牌 (v3.0)")
async def refresh_transaction_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    刷新交易令牌 (v3.0 新架構)

    當 Transaction Token 過期(30分鐘)但 Session 仍有效(60分鐘)時,
    自動重新查詢資料庫權限,建立新的 Token。

    這個 API 會在前端攔截器中自動呼叫,使用者無感知。

    需要提供 Bearer Token (session_id)

    Returns:
        {
            "txn_token": "新的交易令牌",
            "message": "Token 已刷新"
        }
    """
    # 取得 session_id
    session_id = getattr(current_user, 'current_session_id', None)
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無法取得 Session ID,請重新登入"
        )

    # 重新查詢使用者的角色權限 (從資料庫)
    from app.models.roleright import RoleRight
    from app.models.systemfunction import SystemFunction
    from app.core.transaction_token_redis import create_all_functions_token

    role_ids = current_user.user_role if isinstance(current_user.user_role, list) else []

    # 取得使用者所有有權限的功能 (包含權限詳情)
    all_permissions = {}  # {system_function_id: {func_code, module_code, create, read, ...}}

    if role_ids:
        # 查詢所有角色權限
        role_rights = db.query(RoleRight).filter(
            RoleRight.user_role_id.in_(role_ids),
            RoleRight.is_read == True  # 至少要有讀取權限
        ).all()

        # 查詢功能資訊
        function_ids = list(set([rr.system_function_id for rr in role_rights if rr.system_function_id]))
        functions = db.query(SystemFunction).filter(SystemFunction.id.in_(function_ids)).all()
        function_map = {func.id: func for func in functions}

        # 建立權限字典
        for rr in role_rights:
            func_id = rr.system_function_id
            if func_id not in all_permissions:
                func = function_map.get(func_id)
                if func:
                    all_permissions[str(func_id)] = {
                        "func_code": func.func_code,
                        "module_code": func.module_code,
                        "create": False,
                        "read": False,
                        "update": False,
                        "delete": False,
                        "print": False,
                        "file": False
                    }

            # 合併權限 (多個角色的權限取聯集)
            if func_id in function_map:
                perm = all_permissions[str(func_id)]
                perm["create"] = perm["create"] or rr.is_create
                perm["read"] = perm["read"] or rr.is_read
                perm["update"] = perm["update"] or rr.is_update
                perm["delete"] = perm["delete"] or rr.is_delete
                perm["print"] = perm["print"] or rr.is_print
                perm["file"] = perm["file"] or rr.is_file

    # 建立新的 Transaction Token
    txn_token = create_all_functions_token(
        session_id=session_id,
        all_permissions=all_permissions
    )

    if not txn_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系統錯誤：無法建立 Transaction Token"
        )

    logger.info(
        f"✅ Token 已刷新: User={current_user.id}, "
        f"Session={session_id[:8]}..., Functions={len(all_permissions)}"
    )

    return {
        "txn_token": txn_token,
        "message": "Token 已刷新"
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
    func_code: str | list[str],
    required_permission: str = None,
    one_time_use: bool = False
):
    """
    交易令牌驗證依賴項 (v3.0 新架構)

    用於需要 txn_token 驗證的 API 端點。
    v3.0: 一個 token 包含所有功能權限，自動延長時效。

    Args:
        one_time_use: v3.0 中已廢棄，保留此參數僅用於向後相容

    Args:
        func_code: 功能代碼 (str) 或功能代碼列表 (list[str])
                  支援多個 func_code 用於共用 API (如: ["organizations", "tenant_profile"])
        required_permission: 必要的權限類型 (create/read/update/delete/print/file)
                            如果為 None,只驗證 token 有效性

    Example:
        # Single func_code
        @router.post("/role_rights/save")
        async def save_role_rights(
            data: DataModel,
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_txn_token("role_rights", "update"))
        ):
            # Token 已驗證,且使用者有 update 權限
            ...

        # Multiple func_codes (shared API)
        @router.get("/organizations")
        async def get_organizations(
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_txn_token(["organizations", "tenant_profile"], "read"))
        ):
            # Token 包含所有權限，只要有其中一個功能的權限即可
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

        # 正規化 func_code 為列表
        allowed_func_codes = [func_code] if isinstance(func_code, str) else func_code

        # 驗證 token (v3.0: 使用新的驗證邏輯)
        # 這會自動檢查 session_id 匹配，並延長 token 時效
        try:
            token_info = verify_txn_token(
                txn_token=x_txn_token,
                session_id=session_id,
                func_code=allowed_func_codes[0] if len(allowed_func_codes) == 1 else None,
                module_item=required_permission
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Token 驗證失敗: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="系統錯誤：Token 驗證失敗"
            )

        # v3.0: 從 token 中取得所有權限資訊
        all_permissions = token_info.get("permissions", {})

        # 檢查是否有任一功能的權限
        has_func_permission = False
        matched_func_code = None

        for func_code_check in allowed_func_codes:
            # 在所有權限中查找該 func_code
            for func_id, perm in all_permissions.items():
                if perm.get("func_code") == func_code_check:
                    # 找到了這個功能的權限
                    if required_permission:
                        # 檢查是否有指定的權限
                        if perm.get(required_permission, False):
                            has_func_permission = True
                            matched_func_code = func_code_check
                            break
                    else:
                        # 不需要特定權限，只要有這個功能即可
                        has_func_permission = True
                        matched_func_code = func_code_check
                        break

            if has_func_permission:
                break

        if not has_func_permission:
            logger.warning(
                f"[Transaction Token v3.0] 使用者 {current_user.id} Token 有效但缺少權限: "
                f"func_codes={allowed_func_codes}, required_permission={required_permission}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"無權限執行操作"
            )

        logger.debug(
            f"[Transaction Token v3.0] 使用者 {current_user.id} 驗證通過: "
            f"{matched_func_code}" + (f".{required_permission}" if required_permission else "")
        )
        return None

    return dependency
