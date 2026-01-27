"""
Transaction Token Management with Redis (v3.0)
使用 Redis 的交易令牌管理

新架構設計 (v3.0):
- 一個 session 只有一個 transaction token
- Token 包含所有功能的權限資訊
- 登入時同時建立 Session 和 Token
- Token 有效期 30 分鐘，每次使用自動延長 30 分鐘
- Session 有效期 60 分鐘，每次使用自動延長 30 分鐘
"""

import secrets
import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from fastapi import HTTPException, status

from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)

# Token 前綴
TOKEN_PREFIX = "txn_token:"
SESSION_TOKEN_PREFIX = "session_token_mapping:"  # session → token 映射
TOKEN_EXPIRE_SECONDS = 30 * 60  # 30 分鐘（初始時效）
TOKEN_EXTEND_SECONDS = 30 * 60  # 30 分鐘（每次延長）

# 台北時區 (UTC+8)
TAIPEI_TZ = timezone(timedelta(hours=8))


def get_taipei_now():
    """取得台北時間"""
    return datetime.now(timezone.utc).astimezone(TAIPEI_TZ)


def create_all_functions_token(
    session_id: str,
    all_permissions: Dict[int, dict]
) -> str:
    """
    建立包含所有功能權限的 Transaction Token

    Args:
        session_id: Session ID
        all_permissions: 所有功能權限字典
            格式: {
                1: {  # system_function_id
                    "func_code": "organizations",
                    "module_code": "organizations",
                    "create": true,
                    "read": true,
                    ...
                },
                5: {...}
            }

    Returns:
        交易令牌字串
    """
    redis_client = get_redis()
    if not redis_client:
        logger.warning("Redis 未連線，無法建立交易令牌")
        return None

    try:
        # 生成隨機令牌
        random_str = secrets.token_urlsafe(32)
        token_data_str = f"{session_id}:{random_str}:{get_taipei_now().isoformat()}"
        txn_token = hashlib.sha256(token_data_str.encode()).hexdigest()

        # Token 資訊（包含所有功能權限）
        token_info = {
            "session_id": session_id,
            "permissions": all_permissions,
            "created_at": get_taipei_now().isoformat(),
            "last_access": get_taipei_now().isoformat()
        }

        # 儲存 token 資訊
        token_key = f"{TOKEN_PREFIX}{txn_token}"
        redis_client.setex(
            name=token_key,
            time=TOKEN_EXPIRE_SECONDS,
            value=json.dumps(token_info, ensure_ascii=False)
        )

        # 儲存 session → token 的映射
        mapping_key = f"{SESSION_TOKEN_PREFIX}{session_id}"
        redis_client.setex(
            name=mapping_key,
            time=TOKEN_EXPIRE_SECONDS,
            value=txn_token
        )

        logger.info(
            f"✅ 建立交易令牌: session={session_id[:8]}..., "
            f"包含 {len(all_permissions)} 個功能權限, 有效期 30 分鐘"
        )

        return txn_token

    except Exception as e:
        logger.error(f"❌ 建立交易令牌失敗: {e}")
        return None


def verify_txn_token(
    txn_token: str,
    session_id: str,
    func_code: str = None,
    module_item: str = None
) -> dict:
    """
    驗證交易令牌並自動延長有效期

    Args:
        txn_token: 交易令牌
        session_id: Session ID
        func_code: 功能代碼（可選，用於檢查是否有此功能權限）
        module_item: 權限項目（可選，如 "create", "read", "update", "delete"）

    Returns:
        dict: Token 資訊，包含 permissions

    Raises:
        HTTPException: Token 無效、過期、或權限不足
    """
    redis_client = get_redis()
    if not redis_client:
        logger.error("Redis 未連線，無法驗證交易令牌")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系統錯誤：無法連接 Redis"
        )

    token_key = f"{TOKEN_PREFIX}{txn_token}"

    try:
        # 1. 讀取 token 資訊
        token_data = redis_client.get(token_key)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="交易令牌無效或已過期，請重新登入"
            )

        token_info = json.loads(token_data)

        # 2. 檢查 session_id 是否匹配
        if token_info["session_id"] != session_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="交易令牌與 Session 不符，請重新登入"
            )

        # 3. 如果指定了 func_code，檢查是否有該功能的權限
        if func_code:
            permissions = token_info.get("permissions", {})

            # 查找該 func_code 對應的功能權限
            func_permission = None
            for func_id, perm in permissions.items():
                if perm.get("func_code") == func_code:
                    func_permission = perm
                    break

            if not func_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"沒有功能 {func_code} 的使用權限"
                )

            # 4. 如果指定了 module_item，檢查是否有該操作權限
            if module_item:
                # 權限名稱映射 (前端使用 create/read/update/delete，後端存儲使用 is_create/is_read...)
                perm_key_map = {
                    "create": "create",
                    "read": "read",
                    "update": "update",
                    "delete": "delete",
                    "print": "print",
                    "file": "file"
                }

                perm_key = perm_key_map.get(module_item.lower())
                if not perm_key:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"無效的權限項目: {module_item}"
                    )

                has_permission = func_permission.get(perm_key, False)
                if not has_permission:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"沒有 {func_code} 的 {module_item} 權限"
                    )

        # 5. 更新最後存取時間並延長有效期（延長 30 分鐘）
        token_info["last_access"] = get_taipei_now().isoformat()
        redis_client.setex(
            name=token_key,
            time=TOKEN_EXTEND_SECONDS,
            value=json.dumps(token_info, ensure_ascii=False)
        )

        # 6. 同時延長 session → token 映射的有效期
        mapping_key = f"{SESSION_TOKEN_PREFIX}{session_id}"
        redis_client.expire(mapping_key, TOKEN_EXTEND_SECONDS)

        logger.debug(
            f"✅ 交易令牌驗證通過並已延長: session={session_id[:8]}..., "
            f"func_code={func_code}, module_item={module_item}"
        )

        return token_info

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="交易令牌格式錯誤"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 驗證交易令牌失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系統錯誤：無法驗證交易令牌"
        )


def get_session_token(session_id: str) -> Optional[str]:
    """
    取得 session 對應的 transaction token

    Args:
        session_id: Session ID

    Returns:
        Transaction token 或 None
    """
    redis_client = get_redis()
    if not redis_client:
        return None

    try:
        mapping_key = f"{SESSION_TOKEN_PREFIX}{session_id}"
        txn_token = redis_client.get(mapping_key)
        return txn_token if txn_token else None
    except Exception as e:
        logger.error(f"❌ 取得 session token 失敗: {e}")
        return None


def revoke_txn_token(txn_token: str, session_id: str = None) -> bool:
    """
    撤銷交易令牌

    Args:
        txn_token: 交易令牌
        session_id: Session ID（可選，用於同時刪除映射）

    Returns:
        是否撤銷成功
    """
    redis_client = get_redis()
    if not redis_client:
        return False

    try:
        token_key = f"{TOKEN_PREFIX}{txn_token}"
        result = redis_client.delete(token_key)

        # 如果提供了 session_id，也刪除映射
        if session_id:
            mapping_key = f"{SESSION_TOKEN_PREFIX}{session_id}"
            redis_client.delete(mapping_key)

        if result > 0:
            logger.info(f"✅ 交易令牌已撤銷: {txn_token[:16]}...")
            return True
        else:
            logger.warning(f"⚠️  交易令牌不存在: {txn_token[:16]}...")
            return False

    except Exception as e:
        logger.error(f"❌ 撤銷交易令牌失敗: {e}")
        return False


def revoke_session_token(session_id: str) -> bool:
    """
    撤銷某個 session 的 transaction token

    Args:
        session_id: Session ID

    Returns:
        是否撤銷成功
    """
    redis_client = get_redis()
    if not redis_client:
        return False

    try:
        # 1. 取得 session 對應的 token
        mapping_key = f"{SESSION_TOKEN_PREFIX}{session_id}"
        txn_token = redis_client.get(mapping_key)

        if not txn_token:
            logger.warning(f"⚠️  Session 沒有對應的 token: {session_id[:8]}...")
            return False

        # 2. 刪除 token
        token_key = f"{TOKEN_PREFIX}{txn_token}"
        redis_client.delete(token_key)

        # 3. 刪除映射
        redis_client.delete(mapping_key)

        logger.info(f"✅ Session 的交易令牌已撤銷: session={session_id[:8]}...")
        return True

    except Exception as e:
        logger.error(f"❌ 撤銷 session token 失敗: {e}")
        return False


def get_token_info(txn_token: str) -> Optional[dict]:
    """
    取得 token 資訊

    Args:
        txn_token: 交易令牌

    Returns:
        Token 資訊字典，包含 remaining_seconds
    """
    redis_client = get_redis()
    if not redis_client:
        return None

    try:
        token_key = f"{TOKEN_PREFIX}{txn_token}"
        token_data = redis_client.get(token_key)

        if not token_data:
            return None

        token_info = json.loads(token_data)
        ttl = redis_client.ttl(token_key)
        token_info["remaining_seconds"] = max(0, ttl)

        return token_info

    except Exception as e:
        logger.error(f"❌ 取得 token 資訊失敗: {e}")
        return None


def extend_token(txn_token: str, extend_seconds: int = TOKEN_EXTEND_SECONDS) -> bool:
    """
    延長 token 有效期

    Args:
        txn_token: 交易令牌
        extend_seconds: 延長秒數（預設 30 分鐘）

    Returns:
        是否延長成功
    """
    redis_client = get_redis()
    if not redis_client:
        return False

    try:
        token_key = f"{TOKEN_PREFIX}{txn_token}"

        # 檢查 token 是否存在
        if not redis_client.exists(token_key):
            logger.warning(f"⚠️  Token 不存在，無法延長: {txn_token[:16]}...")
            return False

        # 延長有效期
        result = redis_client.expire(token_key, extend_seconds)

        if result:
            logger.debug(f"✅ Token 已延長: {txn_token[:16]}... → {extend_seconds}秒")
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"❌ 延長 token 失敗: {e}")
        return False
