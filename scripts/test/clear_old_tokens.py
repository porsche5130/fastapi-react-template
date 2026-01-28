"""
Clear Old Tokens and Test New Token Creation
清除舊的 Token 並測試新的 Token 建立
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.redis_client import get_redis, init_redis
from app.core.database import SessionLocal
from app.models.systemfunction import SystemFunction
from app.core.transaction_token_redis import get_or_create_function_token
from app.services.session_service import SessionService
import json

# Initialize Redis
init_redis(host="localhost", port=6379, db=0, password="!DC1qaz2wsx")

def clear_old_tokens():
    """清除所有舊的 token"""
    print("=" * 60)
    print("Clearing Old Tokens")
    print("=" * 60)

    redis_client = get_redis()
    if not redis_client:
        print("[FAIL] Redis not connected")
        return False

    # 清除所有 txn_token
    pattern = "txn_token:*"
    count = 0
    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)
        count += 1

    print(f"[SUCCESS] Deleted {count} old tokens")

    # 清除所有 session_func_token mapping
    pattern = "session_func_token:*"
    count = 0
    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)
        count += 1

    print(f"[SUCCESS] Deleted {count} old mappings")

    return True


def test_new_token():
    """測試新的 token 建立（包含 func_code 和 module_code）"""
    print("\n" + "=" * 60)
    print("Testing New Token Creation")
    print("=" * 60)

    redis_client = get_redis()
    db = SessionLocal()

    try:
        # 1. 查詢一個功能
        func = db.query(SystemFunction).filter(
            SystemFunction.func_code == "organizations"
        ).first()

        if not func:
            print("[FAIL] Function 'organizations' not found")
            return False

        print(f"\n[Step 1] Found function: {func.func_code}")
        print(f"  - ID: {func.id}")
        print(f"  - func_code: {func.func_code}")
        print(f"  - module_code: {func.module_code}")

        # 2. 建立測試 session
        session_id = "test_new_token_session"
        SessionService.create_session(
            session_id=session_id,
            user_id=1,
            role_ids=[1],
            organization_id=1,
            username="Test User",
            account="test@example.com",
            authorized_function_ids=[func.id]
        )
        print(f"\n[Step 2] Session created: {session_id}")

        # 3. 建立新的 token（使用新版本的函數）
        print(f"\n[Step 3] Creating token with NEW version...")
        print(f"  Parameters:")
        print(f"    - session_id: {session_id}")
        print(f"    - system_functions_id: {func.id}")
        print(f"    - func_code: {func.func_code}")
        print(f"    - module_code: {func.module_code}")

        token = get_or_create_function_token(
            session_id=session_id,
            system_functions_id=func.id,
            func_code=func.func_code,
            module_code=func.module_code,
            permissions={
                "create": True,
                "read": True,
                "update": True,
                "delete": True,
                "print": False,
                "file": False
            },
            valid_minutes=30
        )

        if not token:
            print("[FAIL] Failed to create token")
            return False

        print(f"[SUCCESS] Token created: {token[:16]}...")

        # 4. 驗證 token 內容
        print(f"\n[Step 4] Verifying token contents...")
        token_key = f"txn_token:{token}"
        token_data = redis_client.get(token_key)

        if not token_data:
            print(f"[FAIL] Token not found in Redis")
            return False

        token_info = json.loads(token_data)
        print("[SUCCESS] Token found in Redis")
        print(f"\nToken Data:")
        print(json.dumps(token_info, indent=2, ensure_ascii=False))

        # 5. 檢查必要欄位
        print(f"\n[Step 5] Checking required fields...")
        required_fields = ["session_id", "system_functions_id", "func_code", "module_code", "permissions"]
        missing_fields = []

        for field in required_fields:
            if field in token_info:
                print(f"  [OK] {field}: {token_info[field]}")
            else:
                print(f"  [MISSING] {field}")
                missing_fields.append(field)

        if missing_fields:
            print(f"\n[FAIL] Missing fields: {missing_fields}")
            print(f"\n⚠️  後端程式碼可能沒有重新載入！")
            print(f"請執行以下步驟:")
            print(f"  1. 停止後端服務 (Ctrl+C)")
            print(f"  2. 重新啟動: uvicorn app.main:app --reload --port 10181")
            return False
        else:
            print(f"\n[SUCCESS] All required fields present!")

        # Cleanup
        print(f"\n[Cleanup] Removing test data...")
        SessionService.delete_session(session_id)
        redis_client.delete(token_key)
        redis_client.delete(f"session_func_token:{session_id}:{func.id}")

        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """主程式"""
    print("\n" + "=" * 60)
    print("Token Cleanup and Test")
    print("=" * 60)

    # Step 1: 清除舊的 token
    if not clear_old_tokens():
        return

    # Step 2: 測試新的 token
    if test_new_token():
        print("\n" + "=" * 60)
        print("[SUCCESS] New token format is working correctly!")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 清除瀏覽器快取")
        print("  2. 重新登入系統")
        print("  3. 進入任一功能頁面")
        print("  4. 檢查 Redis 中的 token 是否包含 func_code 和 module_code")
    else:
        print("\n" + "=" * 60)
        print("[FAIL] Token format verification failed")
        print("=" * 60)
        print("\n請檢查:")
        print("  1. 後端服務是否已重新啟動")
        print("  2. transaction_token_redis.py 的修改是否已生效")


if __name__ == "__main__":
    main()
