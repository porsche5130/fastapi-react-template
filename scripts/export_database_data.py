"""
導出資料庫資料為 INSERT 語法
生成可用於新專案初始化的資料備份 SQL 腳本
"""
import sys
from pathlib import Path
from datetime import datetime

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent / "Develop" / "backend"
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, MetaData, inspect, text
from app.core.database import engine


def format_value(value):
    """格式化值為 SQL 格式"""
    if value is None:
        return 'NULL'
    elif isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, datetime):
        return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
    elif isinstance(value, dict) or isinstance(value, list):
        # JSON 資料
        import json
        return f"'{json.dumps(value, ensure_ascii=False)}'"
    else:
        # 字串資料，需要轉義單引號
        value_str = str(value).replace("'", "''")
        return f"'{value_str}'"


def export_table_data(table_name, conn, f):
    """導出單一資料表的資料"""
    # 查詢資料
    result = conn.execute(text(f"SELECT * FROM {table_name} ORDER BY id;"))
    rows = result.fetchall()

    if not rows:
        f.write(f"-- {table_name}: 無資料\n\n")
        return 0

    # 取得欄位名稱
    columns = list(result.keys())

    f.write(f"-- {table_name} ({len(rows)} 筆資料)\n")
    f.write(f"-- ============================================================================\n\n")

    # 生成 INSERT 語法
    for row in rows:
        # 使用索引存取而非欄位名稱
        values = [format_value(row[i]) for i in range(len(columns))]
        columns_str = ', '.join(columns)
        values_str = ', '.join(values)

        f.write(f"INSERT INTO {table_name} ({columns_str})\n")
        f.write(f"VALUES ({values_str});\n\n")

    return len(rows)


def export_data():
    """導出所有資料表資料"""

    print("="*80)
    print("資料庫資料導出工具 - 生成 INSERT 語法")
    print("="*80)

    # 反射資料庫結構
    metadata = MetaData()
    metadata.reflect(bind=engine)

    tables = sorted(metadata.tables.keys())
    print(f"\n找到 {len(tables)} 個資料表")

    output_file = Path(__file__).parent / "database_seed_data.sql"

    total_rows = 0
    table_stats = {}

    with engine.connect() as conn:
        with open(output_file, 'w', encoding='utf-8') as f:
            # 寫入檔頭
            f.write("-- PA6.4 資料庫初始資料\n")
            f.write(f"-- 自動生成於: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- 使用說明: 在已建立 Schema 的資料庫中執行此腳本以填入初始資料\n\n")
            f.write("-- ============================================================================\n")
            f.write("-- 設定\n")
            f.write("-- ============================================================================\n\n")
            f.write("SET client_encoding = 'UTF8';\n")
            f.write("SET standard_conforming_strings = on;\n\n")

            f.write("-- 暫時停用外鍵檢查 (PostgreSQL 使用 defer)\n")
            f.write("BEGIN;\n\n")

            f.write("-- ============================================================================\n")
            f.write("-- 資料插入\n")
            f.write("-- ============================================================================\n\n")

            # 按依賴順序導出資料
            table_order = [
                'organizations',      # 無依賴
                'users',             # 依賴 organizations
                'user_roles',        # 依賴 users (edit_by)
                'system_functions',  # 無依賴
                'role_rights',       # 依賴 user_roles, system_functions
                'user_logs',         # 依賴 users, system_functions
                'system_codes',      # 無依賴
                'system_notifications',  # 依賴 users
                'notification_closedates',  # 依賴 system_notifications, users
                'notification_read_today',  # 依賴 system_notifications, users
                'file_attachments',  # 依賴 users
                'sequence_rules',    # 依賴 users (edit_by)
                'sequence_values',   # 依賴 sequence_rules
                'sys_profiles',      # 依賴 organizations, users (最後)
            ]

            for table_name in table_order:
                if table_name in metadata.tables:
                    print(f"  導出 {table_name}...")
                    count = export_table_data(table_name, conn, f)
                    table_stats[table_name] = count
                    total_rows += count

            # 更新序列
            f.write("-- ============================================================================\n")
            f.write("-- 更新序列 (SERIAL 欄位)\n")
            f.write("-- ============================================================================\n\n")

            for table_name in table_order:
                if table_name in metadata.tables:
                    table = metadata.tables[table_name]
                    # 檢查是否有 SERIAL 主鍵
                    for column in table.columns:
                        if column.primary_key and column.autoincrement:
                            f.write(f"-- 更新 {table_name} 序列\n")
                            f.write(f"SELECT setval(pg_get_serial_sequence('{table_name}', '{column.name}'), ")
                            f.write(f"COALESCE((SELECT MAX({column.name}) FROM {table_name}), 1), true);\n\n")

            f.write("COMMIT;\n\n")
            f.write("-- 資料導出完成\n")

    print(f"\nSchema 已導出到: {output_file}")
    print(f"檔案大小: {output_file.stat().st_size} bytes")
    print(f"\n資料統計:")
    print(f"  總計: {total_rows} 筆")
    for table_name, count in table_stats.items():
        if count > 0:
            print(f"  - {table_name}: {count} 筆")

    return output_file


if __name__ == "__main__":
    try:
        output_file = export_data()
        print("\n" + "="*80)
        print("SUCCESS!")
        print("="*80)
        print("\n使用方式:")
        print("  1. 先執行 database_schema.sql 建立資料表")
        print("  2. 再執行 database_seed_data.sql 填入資料")
        print("\n範例:")
        print("  psql -U user -d dbname -f scripts/database_schema.sql")
        print("  psql -U user -d dbname -f scripts/database_seed_data.sql")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
