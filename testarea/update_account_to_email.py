"""
更新 user_detail.account 為電子郵件格式
並更新 admin 帳號
"""

import psycopg2

# 資料庫連線設定
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'dev',
    'password': 'dev123',
    'database': 'pa64_dev'
}

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("=" * 70)
    print("更新 user_detail.account 為電子郵件格式")
    print("=" * 70)

    # 1. 檢查當前 admin 帳號
    print("\n[1] 檢查當前 admin 帳號")
    cursor.execute("SELECT id, account, username FROM user_detail WHERE id = 1;")
    user = cursor.fetchone()
    if user:
        print(f"ID: {user[0]}")
        print(f"當前帳號: {user[1]}")
        print(f"使用者名稱: {user[2]}")

    # 2. 更新 admin 帳號為電子郵件
    print("\n[2] 更新 admin 帳號為電子郵件")
    new_email = "admin@pa64.system"

    cursor.execute(
        "UPDATE user_detail SET account = %s WHERE id = 1;",
        (new_email,)
    )
    conn.commit()
    print(f"✓ 帳號已更新為: {new_email}")

    # 3. 驗證更新
    print("\n[3] 驗證更新")
    cursor.execute("SELECT id, account, username FROM user_detail WHERE id = 1;")
    user = cursor.fetchone()
    if user:
        print(f"ID: {user[0]}")
        print(f"新帳號: {user[1]}")
        print(f"使用者名稱: {user[2]}")

    # 4. 顯示所有使用者帳號
    print("\n[4] 所有使用者帳號")
    cursor.execute("SELECT id, account, username FROM user_detail ORDER BY id;")
    users = cursor.fetchall()
    for user in users:
        print(f"  [{user[0]}] {user[1]} - {user[2]}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 70)
    print("更新完成！")
    print("=" * 70)
    print(f"\n新的登入帳號: {new_email}")
    print("密碼: admin123")

if __name__ == "__main__":
    main()
