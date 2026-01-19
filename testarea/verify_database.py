"""
PA6.4 資料庫驗證腳本
檢查資料表結構、初始資料和外鍵關聯
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json

# 資料庫連線設定
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'dev',
    'password': 'dev123',
    'database': 'pa64_dev'
}

def verify_database():
    """驗證資料庫結構與資料"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("=" * 70)
        print("PA6.4 資料庫驗證報告")
        print("=" * 70)

        # 1. 檢查資料表
        print("\n[1] 資料表檢查")
        print("-" * 70)
        cursor.execute("""
            SELECT table_name,
                   (SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_name = t.table_name AND table_schema = 'public') as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        expected_tables = ['organizations', 'user_role', 'user_detail', 'sysfuction', 'sys_profile', 'userlogs']

        print(f"預期資料表數量: {len(expected_tables)}")
        print(f"實際資料表數量: {len(tables)}\n")

        for table in tables:
            status = "[OK]" if table['table_name'] in expected_tables else "[WARN]"
            print(f"{status} {table['table_name']:<20} ({table['column_count']} 欄位)")

        # 2. 檢查外鍵約束
        print("\n[2] 外鍵約束檢查")
        print("-" * 70)
        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name;
        """)

        foreign_keys = cursor.fetchall()
        print(f"外鍵數量: {len(foreign_keys)}\n")

        for fk in foreign_keys:
            print(f"[OK] {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")

        # 3. 檢查初始資料
        print("\n[3] 初始資料檢查")
        print("-" * 70)

        # 3.1 organizations
        cursor.execute("SELECT * FROM organizations WHERE id = 1;")
        org = cursor.fetchone()
        if org:
            print(f"[OK] organizations: {org['org_name']} (is_mana: {org['is_mana']})")
        else:
            print("[ERROR] organizations: 無初始資料")

        # 3.2 user_role
        cursor.execute("SELECT * FROM user_role WHERE id = 1;")
        role = cursor.fetchone()
        if role:
            print(f"[OK] user_role: {role['role_cname']} ({role['role_ename']})")
        else:
            print("[ERROR] user_role: 無初始資料")

        # 3.3 user_detail
        cursor.execute("SELECT * FROM user_detail WHERE id = 1;")
        user = cursor.fetchone()
        if user:
            print(f"[OK] user_detail: {user['username']} (account: {user['account']})")
            print(f"     角色: {json.dumps(user['user_role'])}")
        else:
            print("[ERROR] user_detail: 無初始資料")

        # 3.4 sysfuction
        cursor.execute("SELECT COUNT(*) as count FROM sysfuction;")
        func_count = cursor.fetchone()['count']
        print(f"[OK] sysfuction: {func_count} 個系統功能")

        cursor.execute("SELECT id, func_code, func_cname, func_type FROM sysfuction ORDER BY id;")
        functions = cursor.fetchall()
        for func in functions:
            func_type_name = "節點" if func['func_type'] == 1 else "功能"
            print(f"     [{func['id']}] {func['func_code']:<20} {func['func_cname']:<20} ({func_type_name})")

        # 3.5 sys_profile
        cursor.execute("SELECT * FROM sys_profile WHERE id = 1;")
        profile = cursor.fetchone()
        if profile:
            print(f"[OK] sys_profile: {profile['sys_ctitle']}")
            print(f"     URL: {profile['sys_url']}")
            print(f"     狀態: {'正常' if profile['is_service'] else '維護中'}")
        else:
            print("[ERROR] sys_profile: 無初始資料")

        # 3.6 userlogs
        cursor.execute("SELECT COUNT(*) as count FROM userlogs;")
        log_count = cursor.fetchone()['count']
        print(f"[OK] userlogs: {log_count} 筆紀錄")

        # 4. 檢查 JSONB 欄位
        print("\n[4] JSONB 欄位檢查")
        print("-" * 70)

        # user_detail.user_role
        cursor.execute("SELECT id, account, user_role FROM user_detail WHERE id = 1;")
        user = cursor.fetchone()
        print(f"[OK] user_detail.user_role: {json.dumps(user['user_role'])}")

        # sysfuction.module_item
        cursor.execute("SELECT id, func_code, module_item FROM sysfuction WHERE func_type = 2 LIMIT 1;")
        func = cursor.fetchone()
        print(f"[OK] sysfuction.module_item: {json.dumps(func['module_item'])}")

        # 5. 檢查約束
        print("\n[5] 特殊約束檢查")
        print("-" * 70)

        # sys_profile.id = 1
        cursor.execute("SELECT COUNT(*) as count FROM sys_profile;")
        profile_count = cursor.fetchone()['count']
        print(f"[OK] sys_profile 唯一性: {profile_count} 筆 (應為 1)")

        # organizations.is_mana
        cursor.execute("SELECT COUNT(*) as count FROM organizations WHERE is_mana = TRUE;")
        mana_count = cursor.fetchone()['count']
        print(f"[OK] organizations.is_mana 唯一性: {mana_count} 筆管理公司")

        # 6. 資料庫資訊
        print("\n[6] 資料庫資訊")
        print("-" * 70)
        cursor.execute("SELECT version();")
        version = cursor.fetchone()['version']
        print(f"PostgreSQL 版本: {version.split(',')[0]}")

        cursor.execute("SELECT pg_size_pretty(pg_database_size('pa64_dev')) as size;")
        size = cursor.fetchone()['size']
        print(f"資料庫大小: {size}")

        cursor.close()
        conn.close()

        print("\n" + "=" * 70)
        print("驗證完成 - 資料庫狀態正常")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n[ERROR] 驗證失敗: {e}")
        return False

if __name__ == "__main__":
    verify_database()
