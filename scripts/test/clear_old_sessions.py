"""
清除舊的 Session（沒有 authorized_function_ids 的 Session）
"""
import redis
import json

# 連接 Redis
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    password='!DC1qaz2wsx',
    decode_responses=True
)

print("=" * 60)
print("清除舊 Session")
print("=" * 60)

# 搜尋所有 session
pattern = "session:*"
deleted_count = 0

for key in r.scan_iter(match=pattern):
    session_json = r.get(key)
    if session_json:
        try:
            session_data = json.loads(session_json)
            # 檢查是否有 authorized_function_ids
            if 'authorized_function_ids' not in session_data:
                print(f"刪除舊 Session: {key}")
                r.delete(key)
                deleted_count += 1
            else:
                print(f"保留新 Session: {key} (有 {len(session_data['authorized_function_ids'])} 個授權功能)")
        except json.JSONDecodeError:
            print(f"刪除無效 Session: {key}")
            r.delete(key)
            deleted_count += 1

print("=" * 60)
print(f"已刪除 {deleted_count} 個舊 Session")
print("=" * 60)
print("\n請重新登入以建立新的 Session")
