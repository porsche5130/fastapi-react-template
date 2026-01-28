"""
檢查 Redis 中的交易令牌資料
"""
import redis
import json
from datetime import datetime
import sys

# 設置輸出編碼
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# 連線到 Redis
r = redis.Redis(
    host='10.1.0.20',
    port=6379,
    db=1,
    password='!DC1qaz2wsx',
    decode_responses=True
)

print("=" * 80)
print("Redis 資料檢查 - PA6.4 專案 (DB 1)")
print("=" * 80)

# 測試連線
try:
    ping = r.ping()
    print(f"[OK] Redis 連線成功: {ping}")
except Exception as e:
    print(f"[ERROR] Redis 連線失敗: {e}")
    exit(1)

# 查看所有 keys
print("\n" + "=" * 80)
print("1. 所有 Keys 列表")
print("=" * 80)
all_keys = r.keys("*")
print(f"總共有 {len(all_keys)} 個 keys\n")

if all_keys:
    # 依類型分組
    session_keys = [k for k in all_keys if k.startswith("session:")]
    token_keys = [k for k in all_keys if k.startswith("txn_token:")]
    other_keys = [k for k in all_keys if not k.startswith("session:") and not k.startswith("txn_token:")]

    print(f"Session Keys: {len(session_keys)}")
    print(f"Token Keys: {len(token_keys)}")
    print(f"Other Keys: {len(other_keys)}")
    print()

    # 顯示所有 keys
    for key in all_keys[:20]:  # 只顯示前 20 個
        key_type = r.type(key)
        ttl = r.ttl(key)
        ttl_info = f"{ttl}s" if ttl > 0 else ("永久" if ttl == -1 else "已過期")
        print(f"  - {key} ({key_type}, TTL: {ttl_info})")

    if len(all_keys) > 20:
        print(f"  ... 還有 {len(all_keys) - 20} 個 keys")

# 檢查 Session 資料
print("\n" + "=" * 80)
print("2. Session 資料")
print("=" * 80)
session_keys = r.keys("session:*")
print(f"找到 {len(session_keys)} 個 session\n")

for key in session_keys[:5]:  # 顯示前 5 個
    data = r.get(key)
    ttl = r.ttl(key)
    print(f"Key: {key}")
    print(f"TTL: {ttl}s ({ttl/3600:.1f} 小時)")
    if data:
        try:
            session_data = json.loads(data)
            print(f"User ID: {session_data.get('user_id')}")
            print(f"Organization ID: {session_data.get('organization_id')}")
            print(f"Username: {session_data.get('username')}")
            print(f"Permissions: {len(session_data.get('permissions', []))} 個")
        except:
            print(f"Data: {data[:100]}...")
    print()

# 檢查 Transaction Token 資料
print("=" * 80)
print("3. Transaction Token 資料")
print("=" * 80)
token_keys = r.keys("txn_token:*")
print(f"找到 {len(token_keys)} 個交易令牌\n")

if token_keys:
    for key in token_keys[:10]:  # 顯示前 10 個
        data = r.get(key)
        ttl = r.ttl(key)
        print(f"Key: {key}")
        print(f"TTL: {ttl}s ({ttl/60:.1f} 分鐘)")
        if data:
            try:
                token_data = json.loads(data)
                print(f"Session ID: {token_data.get('session_id')}")
                print(f"User ID: {token_data.get('user_id')}")
                print(f"Organization ID: {token_data.get('organization_id')}")
                print(f"Permissions: {token_data.get('permissions', [])}")
                created_at = token_data.get('created_at')
                if created_at:
                    print(f"Created: {created_at}")
            except Exception as e:
                print(f"Data (無法解析 JSON): {data[:100]}...")
                print(f"Error: {e}")
        print()
else:
    print("[WARNING] 沒有找到任何交易令牌!")
    print("\n可能的原因:")
    print("1. 還沒有任何使用者登入並進行操作")
    print("2. 所有的交易令牌都已過期")
    print("3. Token 使用了不同的 key 前綴")

# 檢查其他 keys
print("=" * 80)
print("4. 其他 Keys")
print("=" * 80)
other_keys = [k for k in all_keys if not k.startswith("session:") and not k.startswith("txn_token:")]
print(f"找到 {len(other_keys)} 個其他類型的 key\n")

for key in other_keys[:10]:
    key_type = r.type(key)
    ttl = r.ttl(key)
    print(f"Key: {key}")
    print(f"Type: {key_type}")
    print(f"TTL: {ttl}s")

    if key_type == "string":
        data = r.get(key)
        if data:
            print(f"Data: {data[:100]}...")
    elif key_type == "hash":
        data = r.hgetall(key)
        print(f"Fields: {list(data.keys())[:5]}")
    elif key_type == "list":
        length = r.llen(key)
        print(f"Length: {length}")
    elif key_type == "set":
        size = r.scard(key)
        print(f"Size: {size}")
    print()

# 記憶體使用
print("=" * 80)
print("5. Redis 記憶體資訊")
print("=" * 80)
info = r.info("memory")
print(f"Used Memory: {info['used_memory_human']}")
print(f"Used Memory Peak: {info['used_memory_peak_human']}")
print(f"Total System Memory: {info.get('total_system_memory_human', 'N/A')}")

print("\n" + "=" * 80)
print("檢查完成")
print("=" * 80)
