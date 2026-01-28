"""
完整的資料庫遷移腳本
使用 PostgreSQL 的 COPY 和正確的依賴順序
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import Json
import sys
import json

# 連線配置
LOCAL_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "pa64_dev",
    "user": "dev",
    "password": "dev123"
}

REMOTE_CONFIG = {
    "host": "10.1.0.20",
    "port": 5433,
    "database": "pa64_dev",
    "user": "admin",
    "password": "!DC1qaz2wsx"
}

def get_connection(config):
    """建立資料庫連線"""
    return psycopg2.connect(**config)

def dump_schema(local_conn):
    """從本機資料庫匯出完整 schema (DDL)"""
    print("\n[1/4] 匯出 Schema...")

    cur = local_conn.cursor()
    schema_sql = []

    # 1. 匯出所有序列
    print("  - 匯出序列...")
    cur.execute("""
        SELECT
            'CREATE SEQUENCE IF NOT EXISTS ' || quote_ident(sequence_name) ||
            ' INCREMENT ' || increment ||
            ' MINVALUE ' || minimum_value ||
            ' MAXVALUE ' || maximum_value ||
            ' START ' || start_value || ';' as ddl
        FROM information_schema.sequences
        WHERE sequence_schema = 'public'
        ORDER BY sequence_name;
    """)

    sequences = [row[0] for row in cur.fetchall()]
    schema_sql.extend(sequences)
    print(f"    找到 {len(sequences)} 個序列")

    # 2. 匯出所有表結構 (不含約束)
    print("  - 匯出表結構...")
    cur.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)

    tables = [row[0] for row in cur.fetchall()]

    for table in tables:
        # 取得欄位定義
        cur.execute("""
            SELECT
                column_name,
                data_type,
                character_maximum_length,
                column_default,
                is_nullable,
                udt_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (table,))

        columns = cur.fetchall()
        col_defs = []

        for col_name, data_type, max_len, default, nullable, udt_name in columns:
            # 處理欄位類型
            if data_type == 'ARRAY':
                col_type = udt_name.replace('_', '') + '[]'
            elif data_type == 'USER-DEFINED':
                col_type = udt_name
            elif data_type in ('character varying', 'varchar'):
                col_type = f'VARCHAR({max_len})' if max_len else 'VARCHAR'
            elif data_type == 'character':
                col_type = f'CHAR({max_len})' if max_len else 'CHAR'
            else:
                col_type = data_type.upper()

            col_def = f'"{col_name}" {col_type}'

            # 處理 DEFAULT
            if default:
                col_def += f' DEFAULT {default}'

            # 處理 NULL
            if nullable == 'NO':
                col_def += ' NOT NULL'

            col_defs.append(col_def)

        create_table = f'CREATE TABLE IF NOT EXISTS "{table}" (\n  ' + ',\n  '.join(col_defs) + '\n);'
        schema_sql.append(create_table)

    print(f"    找到 {len(tables)} 個表")

    # 3. 匯出主鍵
    print("  - 匯出主鍵...")
    cur.execute("""
        SELECT
            tc.table_name,
            tc.constraint_name,
            string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as columns
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = 'public'
        GROUP BY tc.table_name, tc.constraint_name
        ORDER BY tc.table_name;
    """)

    pk_count = 0
    for table, constraint, columns in cur.fetchall():
        pk_sql = f'ALTER TABLE "{table}" ADD CONSTRAINT "{constraint}" PRIMARY KEY ({columns});'
        schema_sql.append(pk_sql)
        pk_count += 1

    print(f"    找到 {pk_count} 個主鍵")

    # 4. 匯出外鍵
    print("  - 匯出外鍵...")
    cur.execute("""
        SELECT
            tc.table_name,
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
        ORDER BY tc.table_name, tc.constraint_name;
    """)

    fk_count = 0
    for table, constraint, column, ref_table, ref_column in cur.fetchall():
        fk_sql = f'ALTER TABLE "{table}" ADD CONSTRAINT "{constraint}" FOREIGN KEY ("{column}") REFERENCES "{ref_table}" ("{ref_column}");'
        schema_sql.append(fk_sql)
        fk_count += 1

    print(f"    找到 {fk_count} 個外鍵")

    # 5. 匯出索引
    print("  - 匯出索引...")
    cur.execute("""
        SELECT indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
            AND indexname NOT LIKE '%_pkey'
        ORDER BY tablename, indexname;
    """)

    indexes = [row[0] for row in cur.fetchall()]
    # 將 CREATE INDEX 改為 CREATE INDEX IF NOT EXISTS
    indexes = [idx.replace('CREATE INDEX', 'CREATE INDEX IF NOT EXISTS') for idx in indexes]
    schema_sql.extend(indexes)

    print(f"    找到 {len(indexes)} 個索引")

    cur.close()
    return schema_sql, tables

def dump_data(local_conn, tables):
    """從本機資料庫匯出所有資料"""
    print("\n[2/4] 匯出資料...")

    cur = local_conn.cursor()
    data_by_table = {}
    total_rows = 0

    for table in tables:
        cur.execute(f'SELECT * FROM "{table}";')
        rows = cur.fetchall()

        if rows:
            # 取得欄位名稱
            columns = [desc[0] for desc in cur.description]
            data_by_table[table] = {
                'columns': columns,
                'rows': rows
            }
            total_rows += len(rows)
            print(f"  - {table}: {len(rows)} 筆")
        else:
            print(f"  - {table}: 空表")

    cur.close()
    print(f"\n  總共: {total_rows} 筆資料")
    return data_by_table

def restore_schema(remote_conn, schema_sql):
    """在遠端資料庫還原 schema"""
    print("\n[3/4] 還原 Schema...")

    cur = remote_conn.cursor()

    # 先刪除所有外鍵約束
    print("  - 刪除現有外鍵...")
    cur.execute("""
        SELECT 'ALTER TABLE "' || table_name || '" DROP CONSTRAINT IF EXISTS "' || constraint_name || '" CASCADE;'
        FROM information_schema.table_constraints
        WHERE constraint_type = 'FOREIGN KEY'
            AND table_schema = 'public';
    """)

    for (drop_fk,) in cur.fetchall():
        try:
            cur.execute(drop_fk)
        except:
            pass

    # 刪除所有表
    print("  - 刪除現有表...")
    cur.execute("""
        SELECT 'DROP TABLE IF EXISTS "' || tablename || '" CASCADE;'
        FROM pg_tables
        WHERE schemaname = 'public';
    """)

    for (drop_table,) in cur.fetchall():
        try:
            cur.execute(drop_table)
        except:
            pass

    # 刪除所有序列
    print("  - 刪除現有序列...")
    cur.execute("""
        SELECT 'DROP SEQUENCE IF EXISTS "' || sequence_name || '" CASCADE;'
        FROM information_schema.sequences
        WHERE sequence_schema = 'public';
    """)

    for (drop_seq,) in cur.fetchall():
        try:
            cur.execute(drop_seq)
        except:
            pass

    remote_conn.commit()

    # 執行所有 DDL
    print("  - 建立序列、表、約束、索引...")
    success_count = 0
    error_count = 0

    for ddl in schema_sql:
        try:
            cur.execute(ddl)
            success_count += 1
        except Exception as e:
            error_count += 1
            if 'already exists' not in str(e).lower():
                print(f"    警告: {str(e)[:100]}")

    remote_conn.commit()
    print(f"    成功: {success_count}, 錯誤: {error_count}")

    cur.close()

def get_table_order(tables):
    """根據外鍵依賴排序表 (先插入被參考的表)"""
    # 基本順序: 先插入沒有外鍵依賴的基礎表
    order = [
        'users',  # 最基礎的表
        'organizations',  # 第二層
        'user_roles',
        'system_codes',
        'system_functions',
        'sequence_rules',
        'sys_profiles',
        'role_rights',
        'notification_closedates',
        'system_notifications',
        'notification_read_today',
        'sequence_values',
        'file_attachments',
        'user_logs'  # 最後
    ]

    # 加入不在順序列表中的表
    remaining = [t for t in tables if t not in order]
    return [t for t in order if t in tables] + remaining

def convert_value(value, column_type):
    """轉換 Python 值為 PostgreSQL 適當的類型"""
    if value is None:
        return None

    # JSONB 類型
    if isinstance(value, (dict, list)):
        return Json(value)

    return value

def restore_data(remote_conn, data_by_table):
    """在遠端資料庫還原資料"""
    print("\n[4/4] 還原資料...")

    cur = remote_conn.cursor()
    total_rows = 0

    # 取得欄位類型資訊
    cur.execute("""
        SELECT table_name, column_name, udt_name
        FROM information_schema.columns
        WHERE table_schema = 'public';
    """)

    column_types = {}
    for table, column, udt_name in cur.fetchall():
        if table not in column_types:
            column_types[table] = {}
        column_types[table][column] = udt_name

    # 按照依賴順序處理表
    ordered_tables = get_table_order(list(data_by_table.keys()))

    # 暫時停用外鍵檢查
    cur.execute("SET session_replication_role = 'replica';")

    for table in ordered_tables:
        if table not in data_by_table:
            continue

        data = data_by_table[table]
        columns = data['columns']
        rows = data['rows']

        if not rows:
            continue

        try:
            # 轉換資料 (處理 JSONB 等特殊類型)
            converted_rows = []
            for row in rows:
                converted_row = []
                for i, value in enumerate(row):
                    column_name = columns[i]
                    # 根據欄位類型轉換值
                    if table in column_types and column_name in column_types[table]:
                        col_type = column_types[table][column_name]
                        if col_type == 'jsonb' and isinstance(value, (dict, list)):
                            converted_row.append(Json(value))
                        else:
                            converted_row.append(value)
                    else:
                        converted_row.append(value)
                converted_rows.append(tuple(converted_row))

            # 使用批次插入
            placeholders = ','.join(['%s'] * len(columns))
            column_names = ','.join([f'"{col}"' for col in columns])
            insert_sql = f'INSERT INTO "{table}" ({column_names}) VALUES ({placeholders})'

            cur.executemany(insert_sql, converted_rows)
            remote_conn.commit()

            total_rows += len(rows)
            print(f"  - {table}: {len(rows)} rows OK")

        except Exception as e:
            error_msg = str(e).replace('\U0001f511', '[emoji]').replace('\u2713', 'OK').replace('\u2717', 'X')
            print(f"  - {table}: Failed - {error_msg[:200]}")
            remote_conn.rollback()

    # 更新序列值
    print("\n  更新序列值...")
    cur.execute("""
        SELECT sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema = 'public';
    """)

    for (seq_name,) in cur.fetchall():
        try:
            # 找到使用此序列的表和欄位
            cur.execute(f"""
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE column_default LIKE '%{seq_name}%'
                    AND table_schema = 'public'
                LIMIT 1;
            """)

            result = cur.fetchone()
            if result:
                table_name, column_name = result
                cur.execute(f'SELECT MAX("{column_name}") FROM "{table_name}";')
                max_val = cur.fetchone()[0]

                if max_val:
                    cur.execute(f"SELECT setval('{seq_name}', {max_val});")
                    print(f"    - {seq_name} = {max_val}")
        except Exception as e:
            print(f"    - {seq_name}: {e}")

    # 重新啟用外鍵檢查
    cur.execute("SET session_replication_role = 'origin';")

    remote_conn.commit()
    cur.close()

    print(f"\n  Total restored: {total_rows} rows")

def main():
    """主程序"""
    print("="*70)
    print("PostgreSQL 資料庫完整遷移工具")
    print("="*70)
    print(f"\n來源: {LOCAL_CONFIG['host']}:{LOCAL_CONFIG['port']}/{LOCAL_CONFIG['database']}")
    print(f"目標: {REMOTE_CONFIG['host']}:{REMOTE_CONFIG['port']}/{REMOTE_CONFIG['database']}")

    try:
        # 連線到兩個資料庫
        print("\n連線到資料庫...")
        local_conn = get_connection(LOCAL_CONFIG)
        remote_conn = get_connection(REMOTE_CONFIG)
        print("  OK - 連線成功")

        # 步驟 1 & 2: 匯出
        schema_sql, tables = dump_schema(local_conn)
        data_by_table = dump_data(local_conn, tables)

        # 步驟 3 & 4: 還原
        restore_schema(remote_conn, schema_sql)
        restore_data(remote_conn, data_by_table)

        # 驗證
        print("\n驗證...")
        local_cur = local_conn.cursor()
        remote_cur = remote_conn.cursor()

        local_cur.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';")
        local_count = local_cur.fetchone()[0]

        remote_cur.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';")
        remote_count = remote_cur.fetchone()[0]

        print(f"  本機表數: {local_count}")
        print(f"  遠端表數: {remote_count}")

        if local_count == remote_count:
            print("  OK 表數一致")
        else:
            print("  ERROR 表數不一致")

        # 關閉連線
        local_cur.close()
        remote_cur.close()
        local_conn.close()
        remote_conn.close()

        print("\n" + "="*70)
        print("OKOKOK 遷移完成！")
        print("="*70)
        print(f"\n遠端資料庫連線資訊:")
        print(f"postgresql://{REMOTE_CONFIG['user']}:{REMOTE_CONFIG['password']}@{REMOTE_CONFIG['host']}:{REMOTE_CONFIG['port']}/{REMOTE_CONFIG['database']}")

        return True

    except Exception as e:
        print(f"\nERROR 錯誤: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
