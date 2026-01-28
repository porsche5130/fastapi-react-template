"""
驗證後端 Redis 連線資訊
"""
import redis

# 連線到 10.1.0.20 DB 1
password = "!DC1qaz2wsx"

print("=== 檢查 Redis 連線資訊 ===\n")

# 測試 DB 0 (舊的配置)
print("測試 DB 0 (localhost 或舊配置):")
try:
    r0 = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r0.ping()
    keys_db0 = r0.dbsize()
    print(f"  localhost:6379 DB 0 - 鍵數: {keys_db0}")
except Exception as e:
    print(f"  localhost:6379 DB 0 - 連線失敗: {e}")

# 測試 10.1.0.20 DB 0
print("\n測試 10.1.0.20 DB 0:")
try:
    r_remote_0 = redis.Redis(host='10.1.0.20', port=6379, db=0, password=password, decode_responses=True)
    r_remote_0.ping()
    keys_remote_0 = r_remote_0.dbsize()
    print(f"  10.1.0.20:6379 DB 0 - 鍵數: {keys_remote_0}")
except Exception as e:
    print(f"  10.1.0.20:6379 DB 0 - 連線失敗: {e}")

# 測試 10.1.0.20 DB 1 (新配置)
print("\n測試 10.1.0.20 DB 1 (應該是後端使用的):")
try:
    r1 = redis.Redis(host='10.1.0.20', port=6379, db=1, password=password, decode_responses=True)
    r1.ping()
    keys_db1 = r1.dbsize()
    print(f"  10.1.0.20:6379 DB 1 - 鍵數: {keys_db1}")

    # 寫入測試鍵
    test_key = 'pa64_connection_test'
    r1.set(test_key, 'backend_connected', ex=300)
    print(f"  已寫入測試鍵: {test_key}")

    # 檢查是否有 session 或 token 相關的鍵
    session_keys = []
    token_keys = []
    for key in r1.scan_iter(match='*', count=100):
        if 'session' in key.lower():
            session_keys.append(key)
        if 'token' in key.lower() or 'txn' in key.lower():
            token_keys.append(key)

    print(f"\n  Session 相關鍵數: {len(session_keys)}")
    print(f"  Token 相關鍵數: {len(token_keys)}")

    if session_keys:
        print(f"  Session 鍵範例: {session_keys[:3]}")
    if token_keys:
        print(f"  Token 鍵範例: {token_keys[:3]}")

except Exception as e:
    print(f"  10.1.0.20:6379 DB 1 - 連線失敗: {e}")

print("\n=== 後端配置資訊 ===")
print("當前設定:")
print("  REDIS_HOST: 10.1.0.20")
print("  REDIS_PORT: 6379")
print("  REDIS_DB: 1")
print("  REDIS_PASSWORD: 已設定")
