"""
監控 Redis 並執行登入測試
"""
import redis
import requests
import json
import time
import sys

# 設置輸出編碼
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Redis 連線
r = redis.Redis(
    host='10.1.0.20',
    port=6379,
    db=1,
    password='!DC1qaz2wsx',
    decode_responses=True
)

print("=" * 80)
print("Redis 監控 & 登入測試")
print("=" * 80)

# 檢查 Redis 連線
try:
    r.ping()
    print("[OK] Redis 連線成功\n")
except Exception as e:
    print(f"[ERROR] Redis 連線失敗: {e}\n")
    exit(1)

# 檢查登入前的 Redis 狀態
print("登入前的 Redis 狀態:")
keys_before = r.keys("*")
print(f"  Keys 數量: {len(keys_before)}")
if keys_before:
    for key in keys_before[:5]:
        print(f"    - {key}")
print()

# 執行登入
print("=" * 80)
print("執行登入...")
print("=" * 80)

API_BASE = "http://localhost:10181"
login_data = {
    "account": "porsche@lab.taipei",
    "password": "1qaz2wsx"
}

try:
    response = requests.post(
        f"{API_BASE}/api/auth/login",
        json=login_data,
        timeout=10
    )

    if response.status_code == 200:
        result = response.json()
        print(f"[OK] 登入成功!")
        print(f"  Access Token: {result.get('access_token', '')[:50]}...")
        print(f"  TXN Token: {result.get('txn_token', '')[:50]}...")

        # 儲存 txn_token 方便後續查詢
        txn_token = result.get('txn_token', '')

        # 等待一下
        print("\n等待 Redis 寫入...")
        time.sleep(2)

        # 檢查登入後的 Redis 狀態
        print("\n" + "=" * 80)
        print("登入後的 Redis 狀態:")
        print("=" * 80)

        keys_after = r.keys("*")
        print(f"\nKeys 數量: {len(keys_after)}")

        if len(keys_after) == 0:
            print("[WARNING] Redis 中仍然沒有資料!")
            print("\n可能的原因:")
            print("1. 後端連接到了不同的 Redis (不同的 host, port, 或 db)")
            print("2. Redis 寫入失敗但沒有報錯")
            print("3. 後端的 Redis 初始化失敗,使用了記憶體儲存")

            # 嘗試檢查其他 DB
            print("\n檢查其他 Redis DB...")
            for db_num in [0, 2, 3]:
                r_other = redis.Redis(
                    host='10.1.0.20',
                    port=6379,
                    db=db_num,
                    password='!DC1qaz2wsx',
                    decode_responses=True
                )
                keys = r_other.keys("*")
                if keys:
                    print(f"  DB {db_num}: {len(keys)} keys")
                    for key in keys[:3]:
                        print(f"    - {key}")
        else:
            print(f"[OK] 新增了 {len(keys_after) - len(keys_before)} 個 keys\n")

            # 顯示新的 keys
            new_keys = set(keys_after) - set(keys_before)
            for key in new_keys:
                key_type = r.type(key)
                ttl = r.ttl(key)
                print(f"  {key}")
                print(f"    Type: {key_type}, TTL: {ttl}s")

                if key_type == "string":
                    data = r.get(key)
                    if data:
                        try:
                            json_data = json.loads(data)
                            print(f"    Data: {json.dumps(json_data, ensure_ascii=False, indent=6)[:200]}...")
                        except:
                            print(f"    Data: {data[:100]}...")
                print()

            # 如果有 txn_token,嘗試直接查詢
            if txn_token:
                token_key = f"txn_token:{txn_token}"
                token_data = r.get(token_key)
                if token_data:
                    print(f"\n找到交易令牌資料: {token_key[:50]}...")
                    print(f"  Data: {token_data[:200]}...")
                else:
                    print(f"\n[WARNING] 未找到交易令牌: {token_key[:50]}...")

    else:
        print(f"[ERROR] 登入失敗: {response.status_code}")
        print(f"  錯誤訊息: {response.text}")

except requests.exceptions.ConnectionError:
    print("[ERROR] 無法連接到後端 API")
    print("  請確認後端服務是否運行在 http://localhost:10181")
except Exception as e:
    print(f"[ERROR] 登入請求失敗: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("測試完成")
print("=" * 80)
