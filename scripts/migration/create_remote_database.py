"""
在遠端 PostgreSQL 建立 pa64_dev 資料庫
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 連線到 postgres 資料庫 (用於建立新資料庫)
host = "10.1.0.20"
port = 5433
admin_db = "postgres"
admin_user = "admin"
admin_password = "!DC1qaz2wsx"

new_db_name = "pa64_dev"
new_db_owner = "admin"

print(f"準備在 {host}:{port} 建立資料庫 '{new_db_name}'")
print("="*60)

try:
    # 連線到 postgres 資料庫
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=admin_db,
        user=admin_user,
        password=admin_password
    )

    # 設定為自動提交模式 (CREATE DATABASE 需要)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # 檢查資料庫是否已存在
    print(f"\n1. 檢查資料庫是否存在...")
    cur.execute("""
        SELECT datname FROM pg_database
        WHERE datname = %s;
    """, (new_db_name,))

    if cur.fetchone():
        print(f"   資料庫 '{new_db_name}' 已存在")
        response = input("   是否要刪除並重建? (yes/no): ").strip().lower()

        if response == 'yes':
            print(f"   正在刪除資料庫 '{new_db_name}'...")
            # 先終止所有連線
            cur.execute(sql.SQL("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid();
            """), [new_db_name])

            # 刪除資料庫
            cur.execute(sql.SQL("DROP DATABASE {}").format(
                sql.Identifier(new_db_name)
            ))
            print(f"   已刪除資料庫 '{new_db_name}'")
        else:
            print("   保留現有資料庫，程式結束")
            cur.close()
            conn.close()
            exit(0)

    # 建立新資料庫
    print(f"\n2. 建立資料庫 '{new_db_name}'...")
    cur.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(
        sql.Identifier(new_db_name),
        sql.Identifier(new_db_owner)
    ))
    print(f"   資料庫建立成功！")

    # 查詢資料庫資訊
    cur.execute("""
        SELECT
            d.datname as name,
            pg_catalog.pg_get_userbyid(d.datdba) as owner,
            pg_catalog.pg_encoding_to_char(d.encoding) as encoding,
            d.datcollate as collate,
            d.datctype as ctype,
            pg_size_pretty(pg_database_size(d.datname)) as size
        FROM pg_catalog.pg_database d
        WHERE d.datname = %s;
    """, (new_db_name,))

    db_info = cur.fetchone()
    if db_info:
        print(f"\n3. 資料庫資訊:")
        print(f"   名稱: {db_info[0]}")
        print(f"   擁有者: {db_info[1]}")
        print(f"   編碼: {db_info[2]}")
        print(f"   Collate: {db_info[3]}")
        print(f"   Ctype: {db_info[4]}")
        print(f"   大小: {db_info[5]}")

    cur.close()
    conn.close()

    # 測試連線到新資料庫
    print(f"\n4. 測試連線到新資料庫...")
    test_conn = psycopg2.connect(
        host=host,
        port=port,
        database=new_db_name,
        user=admin_user,
        password=admin_password
    )

    test_cur = test_conn.cursor()
    test_cur.execute("SELECT current_database(), current_user;")
    db, user = test_cur.fetchone()
    print(f"   連線成功！")
    print(f"   當前資料庫: {db}")
    print(f"   當前使用者: {user}")

    test_cur.close()
    test_conn.close()

    print("\n" + "="*60)
    print("SUCCESS! 資料庫建立完成！")
    print("="*60)

    print(f"\n連線字串:")
    print(f"postgresql://{admin_user}:{admin_password}@{host}:{port}/{new_db_name}")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
