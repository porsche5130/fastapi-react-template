"""
導出完整資料庫 Schema
生成可用於新專案初始化的 SQL 腳本
"""
import sys
from pathlib import Path

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent / "Develop" / "backend"
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.schema import CreateTable, CreateIndex, AddConstraint
from app.core.database import engine


def export_schema():
    """導出資料庫 schema"""

    print("="*80)
    print("資料庫 Schema 導出工具")
    print("="*80)

    # 反射資料庫結構
    metadata = MetaData()
    metadata.reflect(bind=engine)

    tables = sorted(metadata.tables.keys())
    print(f"\n找到 {len(tables)} 個資料表:")
    for table in tables:
        print(f"  - {table}")

    output_file = Path(__file__).parent / "database_schema.sql"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- PA6.4 資料庫 Schema\n")
        f.write("-- 自動生成於: 2026-01-29\n")
        f.write("-- 使用說明: 在空白資料庫中執行此腳本以建立所有資料表\n\n")
        f.write("-- ============================================================================\n")
        f.write("-- 設定\n")
        f.write("-- ============================================================================\n\n")
        f.write("SET client_encoding = 'UTF8';\n")
        f.write("SET standard_conforming_strings = on;\n\n")

        f.write("-- ============================================================================\n")
        f.write("-- 建立資料表\n")
        f.write("-- ============================================================================\n\n")

        # 按順序建立表格（考慮外鍵依賴）
        table_order = [
            'sys_profiles',
            'organizations',
            'users',
            'user_roles',
            'system_functions',
            'role_rights',
            'user_logs',
            'system_codes',
            'system_notifications',
            'notification_closedates',
            'notification_read_today',
            'file_attachments',
            'sequence_rules',
            'sequence_values',
        ]

        for table_name in table_order:
            if table_name in metadata.tables:
                table = metadata.tables[table_name]

                f.write(f"-- {table_name}\n")
                f.write(f"{CreateTable(table).compile(engine)};\n\n")

        # 建立索引
        f.write("-- ============================================================================\n")
        f.write("-- 建立索引\n")
        f.write("-- ============================================================================\n\n")

        for table_name in table_order:
            if table_name in metadata.tables:
                table = metadata.tables[table_name]
                for index in table.indexes:
                    if not index.unique:  # unique 索引通常由 constraint 建立
                        f.write(f"{CreateIndex(index).compile(engine)};\n")

        f.write("\n-- Schema 導出完成\n")

    print(f"\nSchema 已導出到: {output_file}")
    print(f"檔案大小: {output_file.stat().st_size} bytes")

    return output_file


if __name__ == "__main__":
    try:
        output_file = export_schema()
        print("\n" + "="*80)
        print("SUCCESS!")
        print("="*80)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
