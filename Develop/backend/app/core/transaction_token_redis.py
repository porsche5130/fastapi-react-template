"""
Transaction Token Management with Redis
使用 Redis 的交易令牌管理

設計理念:
- Token 綁定 session_id + system_functions_id
- 每個 session 在每個功能只有一個有效 token
- 有效期 30 分鐘，每次使用自動延長
- Session 過期或登出，可撤銷所有相關 token
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
SESSION_FUNCTION_TOKEN_PREFIX = "session_func_token:"  # session + function 對應的 token
TOKEN_EXPIRE_SECONDS = 30 * 60  # 30 分鐘

# 台北時區 (UTC+8)
TAIPEI_TZ = timezone(timedelta(hours=8))


def get_taipei_now():
    """取得台北時間"""
    return datetime.now(timezone.utc).astimezone(TAIPEI_TZ)


def get_or_create_function_token(
    session_id: str,
    system_functions_id: int,
    valid_minutes: int = 30
) -> str:
    """
    取得或建立功能令牌（自動延長機制）

    如果該 session + function 已有有效 token，則延長其有效期
    如果沒有或已過期，則建立新的 token

    Args:
        session_id: Session ID
        system_functions_id: 系統功能 ID
        valid_minutes: 有效期限(分鐘)，預設 30 分鐘

    Returns:
        交易令牌
    """
    redis_client = get_redis()
    if not redis_client:
        logger.warning("Redis 未連線，無法建立交易令牌")
        return None

    try:
        # 1. 檢查是否已有該 session + function 的 token
        mapping_key = f"{SESSION_FUNCTION_TOKEN_PREFIX}{session_id}:{system_functions_id}"
        existing_token = redis_client.get(mapping_key)

        if existing_token:
            # 檢查 token 是否仍然有效
            token_key = f"{TOKEN_PREFIX}{existing_token}"
            token_data = redis_client.get(token_key)

            if token_data:
                # Token 仍然有效，延長有效期
                redis_client.expire(token_key, valid_minutes * 60)
                redis_client.expire(mapping_key, valid_minutes * 60)

                logger.info(
                    f"延長交易令牌有效期: session={session_id[:8]}..., "
                    f"function_id={system_functions_id}, 延長至 {valid_minutes} 分鐘"
                )
                return existing_token

        # 2. 建立新的 token
        random_str = secrets.token_urlsafe(32)
        token_data_str = f"{session_id}:{system_functions_id}:{random_str}:{get_taipei_now().isoformat()}"
        txn_token = hashlib.sha256(token_data_str.encode()).hexdigest()

        # Token 資訊
        token_info = {
            "session_id": session_id,
            "system_functions_id": system_functions_id,
            "created_at": get_taipei_now().isoformat(),
            "last_access": get_taipei_now().isoformat()
        }

        # 3. 儲存 token 資訊
        token_key = f"{TOKEN_PREFIX}{txn_token}"
        redis_client.setex(
            name=token_key,
            time=valid_minutes * 60,
            value=json.dumps(token_info)
        )

        # 4. 儲存 session + function → token 的映射
        redis_client.setex(
            name=mapping_key,
            time=valid_minutes * 60,
            value=txn_token
        )

        logger.info(
            f"建立新交易令牌: session={session_id[:8]}..., "
            f"function_id={system_functions_id}, 有效期 {valid_minutes} 分鐘"
        )

        return txn_token

    except Exception as e:
        logger.error(f"建立或延長交易令牌失敗: {e}")
        return None


def generate_txn_token(
    session_id: str,
    func_code: str,
    valid_minutes: int = 30
) -> str:
    """
    生成交易令牌 (舊版相容，建議使用 get_or_create_function_token)

    Args:
        session_id: Session ID (JWT Token)
        func_code: 功能代碼
        valid_minutes: 有效期限(分鐘)

    Returns:
        交易令牌
    """
    redis_client = get_redis()

    # 生成隨機令牌
    random_str = secrets.token_urlsafe(32)
    token_data = f"{session_id}:{func_code}:{random_str}:{get_taipei_now().isoformat()}"

    # 使用 SHA256 產生最終 token
    txn_token = hashlib.sha256(token_data.encode()).hexdigest()

    # Token 資訊
    token_info = {
        "session_id": session_id,
        "func_code": func_code,
        "created_at": get_taipei_now().isoformat(),
        "used": False
    }

    # 儲存到 Redis
    if redis_client:
        try:
            # 1. 儲存 token 資訊
            redis_key = f"{TOKEN_PREFIX}{txn_token}"
            redis_client.setex(
                name=redis_key,
                time=valid_minutes * 60,
                value=json.dumps(token_info)
            )

        except Exception:
            # Redis 失敗時回退到記憶體儲存
            _fallback_generate(session_id, func_code, valid_minutes, txn_token, token_info)
    else:
        _fallback_generate(session_id, func_code, valid_minutes, txn_token, token_info)

    return txn_token


def verify_txn_token(
    txn_token: str,
    session_id: str,
    func_code: str,
    one_time_use: bool = False
) -> bool:
    """
    驗證交易令牌 (檢查 session_id 綁定)
    """
    redis_client = get_redis()
    redis_key = f"{TOKEN_PREFIX}{txn_token}"

    if redis_client:
        try:
            token_data = redis_client.get(redis_key)
            if not token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="交易令牌無效或已過期,請重新申請"
                )
            token_info = json.loads(token_data)
        except (json.JSONDecodeError, HTTPException) as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="交易令牌格式錯誤"
            )
        except Exception:
            return _fallback_verify(txn_token, session_id, func_code, one_time_use)
    else:
        return _fallback_verify(txn_token, session_id, func_code, one_time_use)

    # ★ 核心檢查: Token 的 session_id 是否匹配
    if token_info["session_id"] != session_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="交易令牌與 Session 不符,請重新登入"
        )

    if one_time_use and token_info.get("used"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="交易令牌已使用,請重新申請"
        )

    # 新版 Token 使用 system_functions_id,舊版使用 func_code
    # 如果提供了 func_code 參數且 Token 有 func_code 欄位,則驗證
    if func_code and "func_code" in token_info:
        if token_info["func_code"] != func_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"交易令牌與功能代碼不符"
            )

    if one_time_use and redis_client:
        try:
            redis_client.delete(redis_key)
            session_tokens_key = f"{SESSION_TOKENS_PREFIX}{session_id}"
            redis_client.srem(session_tokens_key, txn_token)
        except Exception:
            pass

    return True


def revoke_txn_token(txn_token: str) -> bool:
    """撤銷交易令牌"""
    redis_client = get_redis()
    redis_key = f"{TOKEN_PREFIX}{txn_token}"

    if redis_client:
        try:
            token_data = redis_client.get(redis_key)
            if token_data:
                token_info = json.loads(token_data)
                session_id = token_info.get("session_id")
                if session_id:
                    session_tokens_key = f"{SESSION_TOKENS_PREFIX}{session_id}"
                    redis_client.srem(session_tokens_key, txn_token)
            result = redis_client.delete(redis_key)
            return result > 0
        except Exception:
            return _fallback_revoke(txn_token)
    else:
        return _fallback_revoke(txn_token)


def revoke_session_tokens(session_id: str) -> int:
    """撤銷某個 session 的所有 token"""
    redis_client = get_redis()
    if not redis_client:
        return 0

    try:
        count = 0
        session_tokens_key = f"{SESSION_TOKENS_PREFIX}{session_id}"
        tokens = redis_client.smembers(session_tokens_key)

        for token in tokens:
            redis_key = f"{TOKEN_PREFIX}{token}"
            redis_client.delete(redis_key)
            count += 1

        redis_client.delete(session_tokens_key)
        return count
    except Exception:
        return 0


def get_token_info(txn_token: str) -> Optional[dict]:
    """取得 token 資訊"""
    redis_client = get_redis()
    redis_key = f"{TOKEN_PREFIX}{txn_token}"

    if redis_client:
        try:
            token_data = redis_client.get(redis_key)
            if not token_data:
                return None
            token_info = json.loads(token_data)
            ttl = redis_client.ttl(redis_key)
            token_info["remaining_seconds"] = max(0, ttl)
            return token_info
        except Exception:
            return _fallback_get_info(txn_token)
    else:
        return _fallback_get_info(txn_token)


# ========== Fallback 記憶體儲存函數 ==========

def _fallback_generate(session_id, func_code, valid_minutes, txn_token, token_info):
    from app.core.transaction_token import _token_store
    expires_at = get_taipei_now() + timedelta(minutes=valid_minutes)
    _token_store[txn_token] = {
        **token_info,
        "expires_at": expires_at
    }


def _fallback_verify(txn_token, session_id, func_code, one_time_use):
    from app.core.transaction_token import _token_store
    if txn_token not in _token_store:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="交易令牌無效或已過期"
        )

    token_info = _token_store[txn_token]
    if get_taipei_now() > token_info["expires_at"]:
        del _token_store[txn_token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="交易令牌已過期"
        )

    if token_info["session_id"] != session_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="交易令牌與 Session 不符"
        )

    if token_info["func_code"] != func_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="交易令牌與功能代碼不符"
        )

    if one_time_use:
        del _token_store[txn_token]

    return True


def _fallback_revoke(txn_token):
    from app.core.transaction_token import _token_store
    if txn_token in _token_store:
        del _token_store[txn_token]
        return True
    return False


def _fallback_get_info(txn_token):
    from app.core.transaction_token import _token_store
    if txn_token not in _token_store:
        return None
    info = _token_store[txn_token].copy()
    info["remaining_seconds"] = int(
        (info["expires_at"] - get_taipei_now()).total_seconds()
    )
    return info
