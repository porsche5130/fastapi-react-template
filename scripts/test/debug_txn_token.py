"""
診斷為何 txn_token 沒有回傳
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")

print("=== 診斷 Transaction Token 問題 ===\n")

# 1. 檢查 Redis 連線
print("1. 檢查 Redis 連線...")
try:
    from app.core.redis_client import get_redis, init_redis
    from app.core.config import settings

    init_redis()
    redis_client = get_redis()

    if redis_client:
        ping_result = redis_client.ping()
        print(f"   ✅ Redis 連線成功: {ping_result}")

        # 測試基本操作
        redis_client.set("test_key", "test_value")
        value = redis_client.get("test_key")
        redis_client.delete("test_key")
        print(f"   ✅ Redis 基本操作正常")
    else:
        print(f"   ❌ Redis 連線失敗: get_redis() 回傳 None")

except Exception as e:
    print(f"   ❌ Redis 連線失敗: {e}")
    import traceback
    traceback.print_exc()

# 2. 檢查 create_all_functions_token 函式
print("\n2. 測試 create_all_functions_token 函式...")
try:
    from app.core.transaction_token_redis import create_all_functions_token
    import uuid

    # 建立測試 session_id 和權限
    test_session_id = str(uuid.uuid4())
    test_permissions = {
        "1": {
            "func_code": "organizations",
            "module_code": "organizations",
            "create": True,
            "read": True,
            "update": True,
            "delete": True,
            "print": False,
            "file": False
        },
        "2": {
            "func_code": "users",
            "module_code": "users",
            "create": True,
            "read": True,
            "update": True,
            "delete": True,
            "print": False,
            "file": False
        }
    }

    print(f"   測試參數:")
    print(f"   - session_id: {test_session_id}")
    print(f"   - permissions: {len(test_permissions)} 個功能")

    txn_token = create_all_functions_token(
        session_id=test_session_id,
        all_permissions=test_permissions
    )

    if txn_token:
        print(f"   ✅ Token 建立成功")
        print(f"   - txn_token: {txn_token[:32]}...")
        print(f"   - 長度: {len(txn_token)}")

        # 檢查 Redis 中是否有資料
        redis_client = get_redis()
        token_key = f"txn_token:{txn_token}"
        token_data = redis_client.get(token_key)

        if token_data:
            print(f"   ✅ Token 已儲存到 Redis")
            import json
            token_info = json.loads(token_data)
            print(f"   - 權限數量: {len(token_info['permissions'])}")
        else:
            print(f"   ❌ Token 沒有儲存到 Redis")

    else:
        print(f"   ❌ Token 建立失敗: 回傳 None")
        print(f"   可能原因:")
        print(f"   - Redis 未連線")
        print(f"   - create_all_functions_token 函式有問題")

except Exception as e:
    print(f"   ❌ 測試失敗: {e}")
    import traceback
    traceback.print_exc()

# 3. 檢查最近的登入記錄
print("\n3. 檢查 Redis 中的 Session 和 Token...")
try:
    redis_client = get_redis()

    # 列出所有 keys
    session_keys = redis_client.keys("session:*")
    token_keys = redis_client.keys("txn_token:*")
    mapping_keys = redis_client.keys("session_token_mapping:*")

    print(f"   - Session keys: {len(session_keys)}")
    print(f"   - Token keys: {len(token_keys)}")
    print(f"   - Mapping keys: {len(mapping_keys)}")

    if session_keys:
        print(f"\n   最新的 Session:")
        latest_session_key = session_keys[-1]
        session_data = redis_client.get(latest_session_key)
        if session_data:
            import json
            session_info = json.loads(session_data)
            print(f"   - Key: {latest_session_key}")
            print(f"   - User ID: {session_info.get('user_id')}")
            print(f"   - Username: {session_info.get('username')}")

    if mapping_keys:
        print(f"\n   最新的 Token Mapping:")
        latest_mapping_key = mapping_keys[-1]
        txn_token = redis_client.get(latest_mapping_key)
        print(f"   - Key: {latest_mapping_key}")
        print(f"   - Token: {txn_token[:32] if txn_token else 'None'}...")

except Exception as e:
    print(f"   ❌ 檢查失敗: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 診斷完成 ===")
