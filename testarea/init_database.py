"""
PA6.4 系統管理後台資料庫初始化腳本
執行資料表建立與預設資料插入
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 資料庫連線設定
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'dev',
    'password': 'dev123',
    'database': 'pa64_dev'
}

def execute_sql_file(sql_file_path):
    """執行 SQL 檔案"""
    try:
        # 讀取 SQL 檔案
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 連線到資料庫
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("=" * 60)
        print("PA6.4 系統管理後台資料庫初始化")
        print("=" * 60)
        print(f"\n正在執行 SQL 檔案: {sql_file_path}\n")

        # 執行 SQL
        cursor.execute(sql_content)

        print("[OK] SQL 腳本執行成功")

        # 檢查建立的表格
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print("\n已建立的資料表:")
        for table in tables:
            print(f"  - {table[0]}")

        # 檢查各表的記錄數
        print("\n資料表記錄數:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} 筆")

        # 關閉連線
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("資料庫初始化完成")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False

if __name__ == "__main__":
    sql_file = r"W:\P-PA6.4\Develop\backend\init_db_fixed.sql"
    success = execute_sql_file(sql_file)

    if success:
        print("\n[OK] 所有資料表已成功建立")
    else:
        print("\n[ERROR] 資料表建立失敗，請檢查錯誤訊息")
