"""
簡單的資料庫遷移腳本
使用 Python 直接複製表結構和資料
"""
import psycopg2
from psycopg2 import sql

# 本機
local_conn_str = "postgresql://dev:dev123@localhost:5432/pa64_dev"
# 遠端
remote_conn_str = "postgresql://admin:!DC1qaz2wsx@10.1.0.20:5433/pa64_dev"

print("="*70)
print("資料庫遷移工具 (Python Direct Copy)")
print("="*70)

try:
    # 連線
    print("\n[1/5] 連線到資料庫...")
    local_conn = psycopg2.connect(local_conn_str)
    remote_conn = psycopg2.connect(remote_conn_str)

    local_cur = local_conn.cursor()
    remote_cur = remote_conn.cursor()
    print("      OK - Connection successful")

    # 取得所有表
    print("\n[2/5] 取得表列表...")
    local_cur.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)

    tables = [row[0] for row in local_cur.fetchall()]
    print(f"      找到 {len(tables)} 個表: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")

    # 複製每個表
    print("\n[3/5] 複製表結構和資料...")

    for table in tables:
        print(f"      處理表: {table}")

        # 取得建表語句
        local_cur.execute(f"""
            SELECT
                'CREATE TABLE IF NOT EXISTS ' || quote_ident('{table}') || ' AS SELECT * FROM dblink(''host=localhost port=5432 dbname=pa64_dev user=dev password=dev123'', ''SELECT * FROM {table} WHERE 1=0'') AS t(dummy int);'
        """)

        try:
            # 簡單方式：直接使用 CREATE TABLE AS SELECT 從本機複製
            # 但這需要 dblink，所以我們用更直接的方式

            # 先刪除遠端的表（如果存在）
            remote_cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")

            # 取得本機表的 CREATE TABLE 語句
            local_cur.execute(f"""
                SELECT
                    column_name,
                    data_type,
                    character_maximum_length,
                    column_default,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = '{table}'
                ORDER BY ordinal_position;
            """)

            columns_info = local_cur.fetchall()

            # 建構 CREATE TABLE 語句
            col_defs = []
            for col_name, data_type, max_len, default, nullable in columns_info:
                col_def = f"{col_name} {data_type}"

                if max_len and data_type in ('character varying', 'varchar', 'char'):
                    col_def += f"({max_len})"

                if default:
                    col_def += f" DEFAULT {default}"

                if nullable == 'NO':
                    col_def += " NOT NULL"

                col_defs.append(col_def)

            create_sql = f"CREATE TABLE {table} ({', '.join(col_defs)});"
            remote_cur.execute(create_sql)
            print(f"        OK 建立表結構")

            # 複製資料
            local_cur.execute(f"SELECT * FROM {table};")
            rows = local_cur.fetchall()

            if rows:
                # 取得欄位名稱
                column_names = [desc[0] for desc in local_cur.description]

                # 批次插入
                placeholders = ','.join(['%s'] * len(column_names))
                insert_sql = f"INSERT INTO {table} ({','.join(column_names)}) VALUES ({placeholders})"

                remote_cur.executemany(insert_sql, rows)
                print(f"        OK 複製 {len(rows)} 筆資料")
            else:
                print(f"        - 表是空的")

            remote_conn.commit()

        except Exception as e:
            print(f"        ERROR 錯誤: {e}")
            remote_conn.rollback()

    # 複製序列 (sequences)
    print("\n[4/5] 複製序列...")
    local_cur.execute("""
        SELECT sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema = 'public';
    """)

    sequences = local_cur.fetchall()
    for (seq_name,) in sequences:
        print(f"      處理序列: {seq_name}")
        try:
            # 取得當前值
            local_cur.execute(f"SELECT last_value FROM {seq_name};")
            last_val = local_cur.fetchone()[0]

            # 在遠端設定序列值
            remote_cur.execute(f"SELECT setval('{seq_name}', {last_val});")
            remote_conn.commit()
            print(f"        OK 設定值為 {last_val}")

        except Exception as e:
            print(f"        - 序列可能不存在或錯誤: {e}")

    # 驗證
    print("\n[5/5] 驗證...")
    local_cur.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';")
    local_table_count = local_cur.fetchone()[0]

    remote_cur.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';")
    remote_table_count = local_cur.fetchone()[0]

    print(f"      本機表數: {local_table_count}")
    print(f"      遠端表數: {remote_table_count}")

    # 關閉連線
    local_cur.close()
    local_conn.close()
    remote_cur.close()
    remote_conn.close()

    print("\n" + "="*70)
    print("SUCCESS! 遷移完成！")
    print("="*70)

    print(f"\n遠端連線字串:")
    print(f"{remote_conn_str}")

except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
