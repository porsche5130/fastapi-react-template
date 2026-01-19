# -*- coding: utf-8 -*-
"""
PostgreSQL 資料庫連線測試
"""
import sys

def test_postgresql():
    """測試 PostgreSQL 連線和基本操作"""
    print("=" * 60)
    print("PostgreSQL Database Connection Test")
    print("=" * 60)

    # 檢查是否安裝 psycopg2
    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        print("\nERROR: psycopg2 not installed")
        print("\nPlease install:")
        print("  pip install psycopg2-binary")
        return False

    try:
        # 連線資訊
        conn_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'pa64_dev',
            'user': 'dev',
            'password': 'dev123'
        }

        print("\n1. Connecting to PostgreSQL...")
        print(f"   Host: {conn_params['host']}")
        print(f"   Port: {conn_params['port']}")
        print(f"   Database: {conn_params['database']}")
        print(f"   User: {conn_params['user']}")

        # 建立連線
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        print("   OK: Connected successfully!")

        # 取得版本資訊
        print("\n2. Get PostgreSQL version...")
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"   {version}")

        # 取得資料庫資訊
        print("\n3. Get database info...")
        cur.execute("SELECT current_database(), current_user;")
        db_name, db_user = cur.fetchone()
        print(f"   Current database: {db_name}")
        print(f"   Current user: {db_user}")

        # 列出所有表
        print("\n4. List all tables...")
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        if tables:
            print(f"   Found {len(tables)} table(s):")
            for table in tables:
                print(f"     - {table[0]}")
        else:
            print("   No tables found (database is empty)")

        # 測試建立臨時表
        print("\n5. Test CREATE TABLE...")
        cur.execute("""
            CREATE TEMPORARY TABLE test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                data JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        print("   OK: Temporary table created")

        # 測試寫入
        print("\n6. Test INSERT...")
        cur.execute("""
            INSERT INTO test_table (name, data)
            VALUES (%s, %s)
            RETURNING id;
        """, ('Test Project', '{"status": "active", "type": "solar"}'))
        test_id = cur.fetchone()[0]
        print(f"   OK: Inserted record with id={test_id}")

        # 測試讀取
        print("\n7. Test SELECT...")
        cur.execute("SELECT * FROM test_table WHERE id = %s;", (test_id,))
        row = cur.fetchone()
        print(f"   OK: Retrieved record:")
        print(f"       ID: {row[0]}")
        print(f"       Name: {row[1]}")
        print(f"       Data: {row[2]}")
        print(f"       Created: {row[3]}")

        # 測試 JSONB 查詢
        print("\n8. Test JSONB query...")
        cur.execute("""
            SELECT id, name, data->>'status' as status
            FROM test_table
            WHERE data @> '{"status": "active"}';
        """)
        jsonb_row = cur.fetchone()
        print(f"   OK: JSONB query result:")
        print(f"       ID: {jsonb_row[0]}")
        print(f"       Name: {jsonb_row[1]}")
        print(f"       Status: {jsonb_row[2]}")

        # 測試更新
        print("\n9. Test UPDATE...")
        cur.execute("""
            UPDATE test_table
            SET data = jsonb_set(data, '{status}', '"completed"')
            WHERE id = %s
            RETURNING data->>'status';
        """, (test_id,))
        new_status = cur.fetchone()[0]
        print(f"   OK: Updated status to '{new_status}'")

        # 測試刪除
        print("\n10. Test DELETE...")
        cur.execute("DELETE FROM test_table WHERE id = %s;", (test_id,))
        print("   OK: Record deleted")

        # 檢查連線數
        print("\n11. Check connection info...")
        cur.execute("""
            SELECT count(*) FROM pg_stat_activity;
        """)
        total_conn = cur.fetchone()[0]
        cur.execute("""
            SELECT setting FROM pg_settings WHERE name = 'max_connections';
        """)
        max_conn = cur.fetchone()[0]
        print(f"   Current connections: {total_conn}")
        print(f"   Max connections: {max_conn}")

        # 檢查資料庫大小
        print("\n12. Check database size...")
        cur.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database()));
        """)
        db_size = cur.fetchone()[0]
        print(f"   Database size: {db_size}")

        # 關閉連線
        cur.close()
        conn.close()

        print("\n" + "=" * 60)
        print("SUCCESS! All PostgreSQL tests passed!")
        print("=" * 60)

        print("\nConnection strings:")
        print(f"  Local:  postgresql://{conn_params['user']}:{conn_params['password']}@{conn_params['host']}:{conn_params['port']}/{conn_params['database']}")
        print(f"  Docker: postgresql://{conn_params['user']}:{conn_params['password']}@host.docker.internal:{conn_params['port']}/{conn_params['database']}")
        print()

        return True

    except psycopg2.OperationalError as e:
        print(f"\nERROR: Cannot connect to PostgreSQL")
        print(f"Details: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL service is running")
        print("2. Database 'pa64_dev' exists")
        print("3. User 'dev' has correct password")
        print("4. PostgreSQL is listening on localhost:5432")
        return False

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}")
        print(f"Details: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_postgresql()
    sys.exit(0 if success else 1)
