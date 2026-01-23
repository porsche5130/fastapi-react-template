"""
Transaction Token Management
交易令牌管理 - 用於驗證單次交易的安全性
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, status

# 記憶體儲存 token (生產環境建議使用 Redis)
_token_store: Dict[str, dict] = {}


def generate_txn_token(
    user_id: int,
    func_code: str,
    valid_minutes: int = 15
) -> str:
    """
    生成交易令牌

    Args:
        user_id: 使用者 ID
        func_code: 功能代碼
        valid_minutes: 有效期限(分鐘)

    Returns:
        交易令牌
    """
    # 生成隨機令牌
    random_str = secrets.token_urlsafe(32)
    token_data = f"{user_id}:{func_code}:{random_str}:{datetime.utcnow().isoformat()}"

    # 使用 SHA256 產生最終 token
    txn_token = hashlib.sha256(token_data.encode()).hexdigest()

    # 儲存 token 資訊
    expires_at = datetime.utcnow() + timedelta(minutes=valid_minutes)
    _token_store[txn_token] = {
        "user_id": user_id,
        "func_code": func_code,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "used": False
    }

    # 清理過期 token
    _cleanup_expired_tokens()

    return txn_token


def verify_txn_token(
    txn_token: str,
    user_id: int,
    func_code: str,
    one_time_use: bool = False
) -> bool:
    """
    驗證交易令牌

    Args:
        txn_token: 交易令牌
        user_id: 使用者 ID
        func_code: 功能代碼
        one_time_use: 是否為一次性使用(用完即銷毀)

    Returns:
        是否有效

    Raises:
        HTTPException: Token 無效、過期或已使用
    """
    # 檢查 token 是否存在
    if txn_token not in _token_store:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="交易令牌無效"
        )

    token_info = _token_store[txn_token]

    # 檢查是否已過期
    if datetime.utcnow() > token_info["expires_at"]:
        del _token_store[txn_token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="交易令牌已過期，請重新申請"
        )

    # 檢查是否已使用(如果設定為一次性)
    if one_time_use and token_info["used"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="交易令牌已使用"
        )

    # 檢查使用者 ID
    if token_info["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="交易令牌與使用者不符"
        )

    # 檢查功能代碼
    if token_info["func_code"] != func_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="交易令牌與功能代碼不符"
        )

    # 標記為已使用(如果是一次性)
    if one_time_use:
        token_info["used"] = True

    return True


def revoke_txn_token(txn_token: str) -> bool:
    """
    撤銷交易令牌

    Args:
        txn_token: 交易令牌

    Returns:
        是否成功撤銷
    """
    if txn_token in _token_store:
        del _token_store[txn_token]
        return True
    return False


def _cleanup_expired_tokens():
    """清理過期的 token"""
    now = datetime.utcnow()
    expired_tokens = [
        token for token, info in _token_store.items()
        if now > info["expires_at"]
    ]
    for token in expired_tokens:
        del _token_store[token]


def get_token_info(txn_token: str) -> Optional[dict]:
    """
    取得 token 資訊

    Args:
        txn_token: 交易令牌

    Returns:
        Token 資訊 或 None
    """
    if txn_token not in _token_store:
        return None

    info = _token_store[txn_token].copy()
    # 計算剩餘時間
    info["remaining_seconds"] = int(
        (info["expires_at"] - datetime.utcnow()).total_seconds()
    )
    return info
