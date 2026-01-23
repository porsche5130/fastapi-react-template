"""
Transaction Token Management with Redis
使用 Redis 的交易令牌管理

設計理念:
- Token 綁定 session_id (而非 user_id)
- Session_id 綁定 user_id
- 驗證時需同時檢查 session_id 和 token
- Session 過期或登出,可撤銷所有相關 token
"""

import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status

from app.core.redis_client import get_redis

# Token 前綴
TOKEN_PREFIX = "txn_token:"
SESSION_TOKENS_PREFIX = "session_tokens:"  # session 的所有 tokens
TOKEN_EXPIRE_SECONDS = 15 * 60  # 15 分鐘


def generate_txn_token(
    session_id: str,
    func_code: str,
    valid_minutes: int = 15
) -> str:
    """
    生成交易令牌 (綁定 session_id)

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
    token_data = f"{session_id}:{func_code}:{random_str}:{datetime.utcnow().isoformat()}"

    # 使用 SHA256 產生最終 token
    txn_token = hashlib.sha256(token_data.encode()).hexdigest()

    # Token 資訊
    token_info = {
        "session_id": session_id,
        "func_code": func_code,
        "created_at": datetime.utcnow().isoformat(),
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

            # 2. 記錄此 session 的所有 tokens
            session_tokens_key = f"{SESSION_TOKENS_PREFIX}{session_id}"
            redis_client.sadd(session_tokens_key, txn_token)
            redis_client.expire(session_tokens_key, valid_minutes * 60)

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
    expires_at = datetime.utcnow() + timedelta(minutes=valid_minutes)
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
    if datetime.utcnow() > token_info["expires_at"]:
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
        (info["expires_at"] - datetime.utcnow()).total_seconds()
    )
    return info
