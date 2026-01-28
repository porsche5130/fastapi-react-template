"""
Check Redis Session and Token data
"""

from app.core.redis_client import get_redis
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")

redis_client = get_redis()

if not redis_client:
    print("[ERROR] Redis not connected")
    exit(1)

print("=== 檢查 Redis 資料 ===\n")

# 1. 檢查所有 sessions
print("1. Sessions:")
session_keys = list(redis_client.scan_iter(match="session:*"))
print(f"   找到 {len(session_keys)} 個 sessions")

for key in session_keys[:5]:  # 只顯示前 5 個
    session_id = key.replace("session:", "")
    data = redis_client.get(key)
    if data:
        session_data = json.loads(data)
        print(f"\n   Session: {session_id[:16]}...")
        print(f"   - User ID: {session_data.get('user_id')}")
        print(f"   - Username: {session_data.get('username')}")
        print(f"   - Roles: {session_data.get('roles', [])}")
        print(f"   - TTL: {redis_client.ttl(key)} 秒")

# 2. 檢查所有 tokens
print(f"\n\n2. Transaction Tokens:")
token_keys = list(redis_client.scan_iter(match="txn_token:*"))
print(f"   找到 {len(token_keys)} 個 tokens")

for key in token_keys[:5]:  # 只顯示前 5 個
    data = redis_client.get(key)
    if data:
        token_info = json.loads(data)
        print(f"\n   Token: {key[10:26]}...")
        print(f"   - Session ID: {token_info.get('session_id', '')[:16]}...")
        print(f"   - Permissions: {len(token_info.get('permissions', {}))} 個功能")
        print(f"   - TTL: {redis_client.ttl(key)} 秒")

# 3. 檢查 session → token 映射
print(f"\n\n3. Session → Token 映射:")
mapping_keys = list(redis_client.scan_iter(match="session_token_mapping:*"))
print(f"   找到 {len(mapping_keys)} 個映射")

for key in mapping_keys[:5]:
    session_id = key.replace("session_token_mapping:", "")
    token = redis_client.get(key)
    if token:
        print(f"\n   Session: {session_id[:16]}...")
        print(f"   → Token: {token[:16] if isinstance(token, str) else str(token)[:16]}...")
        print(f"   - TTL: {redis_client.ttl(key)} 秒")

# Conclusion
print("\n\n=== Conclusion ===")
if len(session_keys) > 0 and len(token_keys) == 0:
    print("[PROBLEM] Sessions exist but NO Transaction Tokens!")
    print("This means create_all_functions_token() failed during login.")
elif len(session_keys) > 0 and len(token_keys) > 0:
    print("[OK] Both Session and Token exist")
    if len(mapping_keys) == 0:
        print("[WARNING] No session->token mapping found")
else:
    print("[WARNING] No Session or Token found")
