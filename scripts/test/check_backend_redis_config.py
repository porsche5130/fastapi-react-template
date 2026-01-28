"""
檢查後端實際使用的 Redis 配置
"""
import sys
import os

# 設置輸出編碼
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# 加入後端路徑
sys.path.insert(0, os.path.join(os.getcwd(), 'Develop', 'backend'))

# 載入設定
from app.core.config import settings

print("=" * 80)
print("後端實際使用的配置")
print("=" * 80)

print("\nRedis 配置:")
print(f"  REDIS_HOST: {settings.REDIS_HOST}")
print(f"  REDIS_PORT: {settings.REDIS_PORT}")
print(f"  REDIS_DB: {settings.REDIS_DB}")
print(f"  REDIS_PASSWORD: {settings.REDIS_PASSWORD}")

print("\nPostgreSQL 配置:")
print(f"  DATABASE_URL: {settings.DATABASE_URL}")

print("\nApplication 配置:")
print(f"  ENVIRONMENT: {settings.ENVIRONMENT}")
print(f"  DEBUG: {settings.DEBUG}")
print(f"  PORT: {settings.PORT}")

print("\n" + "=" * 80)

# 測試 Redis 連線
from app.core.redis_client import get_redis
import json

print("測試 Redis 連線...")
redis_client = get_redis()

if redis_client:
    print(f"[OK] Redis 連線成功!")

    # 查看所有 keys
    all_keys = redis_client.keys("*")
    print(f"\nRedis 中有 {len(all_keys)} 個 keys")

    if all_keys:
        # 顯示 session keys
        session_keys = [k.decode() if isinstance(k, bytes) else k for k in all_keys if (k.decode() if isinstance(k, bytes) else k).startswith("session:")]
        print(f"  Session keys: {len(session_keys)}")
        for key in session_keys[:3]:
            print(f"    - {key}")

        # 顯示 token keys
        token_keys = [k.decode() if isinstance(k, bytes) else k for k in all_keys if (k.decode() if isinstance(k, bytes) else k).startswith("txn_token:")]
        print(f"  Token keys: {len(token_keys)}")
        for key in token_keys[:3]:
            print(f"    - {key[:50]}...")
else:
    print("[ERROR] Redis 連線失敗!")

print("=" * 80)
