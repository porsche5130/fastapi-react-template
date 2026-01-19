"""
檢查並更新 admin 密碼
"""

import psycopg2
from passlib.context import CryptContext

# 資料庫連線設定
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'dev',
    'password': 'dev123',
    'database': 'pa64_dev'
}

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 查詢當前密碼
    cursor.execute("SELECT id, account, password FROM user_detail WHERE account = 'admin';")
    user = cursor.fetchone()

    if user:
        print(f"使用者 ID: {user[0]}")
        print(f"帳號: {user[1]}")
        print(f"當前密碼 Hash: {user[2]}")
        print(f"Hash 長度: {len(user[2])}")

        # 生成新的密碼 hash
        new_password = "admin123"
        new_hash = pwd_context.hash(new_password)
        print(f"\n新的密碼 Hash: {new_hash}")
        print(f"新 Hash 長度: {len(new_hash)}")

        # 驗證新 hash
        is_valid = pwd_context.verify(new_password, new_hash)
        print(f"新 Hash 驗證: {is_valid}")

        # 更新密碼
        cursor.execute(
            "UPDATE user_detail SET password = %s WHERE id = %s;",
            (new_hash, user[0])
        )
        conn.commit()

        print("\n密碼已更新！")
        print(f"帳號: admin")
        print(f"密碼: admin123")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
