"""
列出資料庫中的測試使用者
"""
import psycopg2
import sys

# 設置輸出編碼
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# 連線到資料庫
conn = psycopg2.connect(
    host='10.1.0.20',
    port=5433,
    database='pa64_dev',
    user='admin',
    password='!DC1qaz2wsx'
)

cursor = conn.cursor()

print("=" * 80)
print("資料庫中的使用者列表")
print("=" * 80)

# 先查詢有哪些資料表
cursor.execute("""
    SELECT tablename
    FROM pg_tables
    WHERE schemaname='public' AND tablename LIKE '%user%'
    ORDER BY tablename
""")
tables = cursor.fetchall()
print("包含 user 的資料表:")
for t in tables:
    print(f"  - {t[0]}")
print()

# 查詢啟用的使用者 (使用 users 資料表)
cursor.execute("""
    SELECT id, account, username, is_active, organization_id, user_role
    FROM users
    WHERE is_active = true
    ORDER BY id
    LIMIT 10
""")

users = cursor.fetchall()

if not users:
    print("沒有找到任何啟用的使用者")
else:
    print(f"\n找到 {len(users)} 個啟用的使用者:\n")
    for user in users:
        user_id, account, username, is_active, org_id, roles = user
        print(f"ID: {user_id}")
        print(f"  帳號: {account}")
        print(f"  姓名: {username}")
        print(f"  組織 ID: {org_id}")
        print(f"  角色 IDs: {roles}")
        print(f"  狀態: {'啟用' if is_active else '停用'}")
        print()

print("=" * 80)
print("提示:")
print("1. 請記下其中一個帳號 (account)")
print("2. 密碼需要詢問管理員或查看測試資料")
print("3. 如果是測試環境,常見密碼可能是: admin123, test123, password123")
print("=" * 80)

cursor.close()
conn.close()
