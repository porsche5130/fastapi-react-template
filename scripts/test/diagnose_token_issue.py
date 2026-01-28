"""
Transaction Token Diagnosis
診斷交易令牌問題
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.redis_client import get_redis, init_redis
from app.core.database import SessionLocal
from app.models.systemfunction import SystemFunction
from app.core.transaction_token_redis import get_or_create_function_token, get_token_info
from app.services.session_service import SessionService
import json

# Initialize Redis
init_redis(host="localhost", port=6379, db=0, password="!DC1qaz2wsx")

def diagnose():
    """診斷交易令牌問題"""
    print("=" * 60)
    print("Transaction Token Diagnosis")
    print("=" * 60)

    # 1. Check Redis connection
    print("\n[Step 1] Checking Redis connection...")
    redis_client = get_redis()
    if not redis_client:
        print("[FAIL] Redis not connected")
        return
    print("[PASS] Redis connected")

    # 2. Check database connection and system_functions table
    print("\n[Step 2] Checking database and system_functions...")
    db = SessionLocal()
    try:
        # Query a function
        func = db.query(SystemFunction).filter(
            SystemFunction.func_code == "role_rights"
        ).first()

        if not func:
            print("[FAIL] system_functions table has no data or 'role_rights' not found")
            return

        print(f"[PASS] Found function: {func.func_code}")
        print(f"  - ID: {func.id}")
        print(f"  - func_cname: {func.func_cname}")
        print(f"  - module_code: {func.module_code}")

        # 3. Create a test session
        print("\n[Step 3] Creating test session...")
        session_id = "diagnose_session_001"
        result = SessionService.create_session(
            session_id=session_id,
            user_id=1,
            role_ids=[1],
            organization_id=1,
            username="Test User",
            account="test@example.com",
            authorized_function_ids=[func.id]
        )

        if not result:
            print("[FAIL] Failed to create session")
            return
        print(f"[PASS] Session created: {session_id}")

        # 4. Create a transaction token
        print("\n[Step 4] Creating transaction token...")
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
            return

        print(f"[PASS] Token created successfully")
        print(f"  Token (first 16 chars): {token[:16]}...")

        # 5. Verify token exists in Redis
        print("\n[Step 5] Verifying token in Redis...")
        token_key = f"txn_token:{token}"
        token_data = redis_client.get(token_key)

        if not token_data:
            print(f"[FAIL] Token not found in Redis with key: {token_key}")
            return

        token_info = json.loads(token_data)
        print("[PASS] Token found in Redis")
        print(f"  Token data: {json.dumps(token_info, indent=2)}")

        # 6. Check token mapping
        print("\n[Step 6] Checking session-function mapping...")
        mapping_key = f"session_func_token:{session_id}:{func.id}"
        mapped_token = redis_client.get(mapping_key)

        if not mapped_token:
            print(f"[FAIL] Mapping not found with key: {mapping_key}")
        else:
            print(f"[PASS] Mapping found")
            print(f"  Mapped token matches: {mapped_token == token}")

        # 7. Get token info using service
        print("\n[Step 7] Getting token info via service...")
        info = get_token_info(token)

        if not info:
            print("[FAIL] get_token_info returned None")
        else:
            print("[PASS] Token info retrieved")
            print(f"  Info: {json.dumps(info, indent=2)}")

        # 8. List all tokens in Redis
        print("\n[Step 8] Listing all tokens in Redis...")
        pattern = "txn_token:*"
        count = 0
        for key in redis_client.scan_iter(match=pattern):
            count += 1
            print(f"  - {key}")
            if count >= 10:
                print("  ... (showing first 10)")
                break

        if count == 0:
            print("  [WARN] No tokens found in Redis")
        else:
            print(f"  Total tokens (scanned): {count}")

        # Cleanup
        print("\n[Cleanup] Removing test data...")
        SessionService.delete_session(session_id)
        redis_client.delete(token_key)
        redis_client.delete(mapping_key)
        print("[DONE] Cleanup complete")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("Diagnosis Complete")
    print("=" * 60)


if __name__ == "__main__":
    diagnose()
