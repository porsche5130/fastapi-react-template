"""
清理 localhost Redis DB 0 中的舊 Session 和 Token 資料
"""
import redis
import sys

# 設置輸出編碼
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

print("=" * 80)
print("清理 localhost Redis DB 0 中的舊資料")
print("=" * 80)

# 連線到 localhost Redis
try:
    r = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )
    r.ping()
    print("[OK] 連線到 localhost:6379 DB 0\n")
except Exception as e:
    print(f"[ERROR] 無法連線到 localhost Redis: {e}")
    exit(1)

# 查看要刪除的 keys
patterns = ["session:*", "txn_token:*", "session_token_mapping:*"]
keys_to_delete = []

for pattern in patterns:
    keys = r.keys(pattern)
    if keys:
        print(f"找到 {len(keys)} 個 {pattern} keys")
        keys_to_delete.extend(keys)

if not keys_to_delete:
    print("\n[INFO] 沒有找到需要清理的資料")
    exit(0)

print(f"\n總共找到 {len(keys_to_delete)} 個 keys 需要清理")
print("\n即將刪除以下 keys:")
for key in keys_to_delete[:10]:
    print(f"  - {key}")
if len(keys_to_delete) > 10:
    print(f"  ... 還有 {len(keys_to_delete) - 10} 個")

# 確認
response = input("\n確定要刪除這些資料嗎? (yes/no): ")
if response.lower() != 'yes':
    print("已取消")
    exit(0)

# 刪除
print("\n正在刪除...")
deleted_count = 0
for key in keys_to_delete:
    try:
        r.delete(key)
        deleted_count += 1
    except Exception as e:
        print(f"[ERROR] 刪除 {key} 失敗: {e}")

print(f"\n[OK] 已刪除 {deleted_count} 個 keys")

# 確認結果
remaining = 0
for pattern in patterns:
    remaining += len(r.keys(pattern))

print(f"剩餘 keys: {remaining}")
print("\n" + "=" * 80)
print("清理完成")
print("=" * 80)
