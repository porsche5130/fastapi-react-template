"""
備份 system_functions 資料表
使用 Python，不需要懂 PostgreSQL 指令
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
import json
from datetime import datetime


def backup_system_functions():
    """備份 system_functions 到 SQL 檔案"""
    engine = create_engine(settings.DATABASE_URL)

    print("正在備份 system_functions 資料表...")

    with engine.connect() as conn:
        # 查詢所有資料
        result = conn.execute(text('''
            SELECT id, func_code, upper_func_id, func_cname, func_ename, func_type,
                   func_order, func_icon, module_code, module_item::text, description,
                   is_mana, is_active, edit_by
            FROM system_functions
            ORDER BY id
        ''')).fetchall()

        print(f"找到 {len(result)} 筆資料")

        # 建立 SQL 內容
        sql_lines = [
            "-- ==========================================",
            "-- system_functions 資料備份",
            f"-- 備份時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"-- 資料筆數: {len(result)}",
            "-- ==========================================\n",
            "-- 使用方式：執行 restore_system_functions.py\n",
            "-- 清空現有資料（小心使用！）",
            "-- TRUNCATE system_functions RESTART IDENTITY CASCADE;\n",
            "-- 插入資料",
            "INSERT INTO system_functions (",
            "    id, func_code, upper_func_id, func_cname, func_ename, func_type,",
            "    func_order, func_icon, module_code, module_item, description,",
            "    is_mana, is_active, edit_by, created_at",
            ") VALUES"
        ]

        # 產生每一筆資料的 INSERT 語句
        for i, row in enumerate(result):
            id_val, func_code, upper_func_id, func_cname, func_ename, func_type, \
            func_order, func_icon, module_code, module_item, description, \
            is_mana, is_active, edit_by = row

            # 處理特殊字元和 NULL 值
            def escape_str(s):
                if s is None:
                    return "NULL"
                # 處理單引號
                s = str(s).replace("'", "''")
                return f"'{s}'"

            func_icon_sql = escape_str(func_icon)
            module_code_sql = escape_str(module_code)
            description_sql = escape_str(description)
            module_item_sql = f"'{module_item}'::jsonb" if module_item else "'[]'::jsonb"

            # 組合 SQL
            values = f"({id_val}, '{func_code}', {upper_func_id}, '{func_cname}', '{func_ename}', {func_type}, {func_order}, {func_icon_sql}, {module_code_sql}, {module_item_sql}, {description_sql}, {is_mana}, {is_active}, {edit_by}, CURRENT_TIMESTAMP)"

            if i < len(result) - 1:
                sql_lines.append(values + ",")
            else:
                sql_lines.append(values + ";")

        # 加入驗證查詢
        sql_lines.extend([
            "\n-- 驗證匯入結果",
            "SELECT COUNT(*) as total_records FROM system_functions;",
            "\n-- 顯示所有功能",
            "SELECT id, func_code, func_cname, module_code, func_order",
            "FROM system_functions",
            "ORDER BY func_order, id;"
        ])

        # 寫入檔案
        backup_file = "../../系統設計/應用系統設計/應用系統基礎功能清冊.SQL"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_lines))

        print(f"\n備份完成！")
        print(f"檔案位置: {backup_file}")
        print(f"備份了 {len(result)} 筆資料")

        # 顯示摘要
        print("\n資料摘要:")
        print("-" * 60)
        for row in result:
            print(f"ID {row[0]:2d}: {row[1]:25s} - {row[3]}")


def show_current_data():
    """顯示目前資料表的內容"""
    engine = create_engine(settings.DATABASE_URL)

    print("\n目前 system_functions 資料表內容:")
    print("=" * 80)

    with engine.connect() as conn:
        result = conn.execute(text('''
            SELECT id, func_code, func_cname, module_code, func_order, is_mana
            FROM system_functions
            ORDER BY func_order, id
        ''')).fetchall()

        print(f"{'ID':3s} | {'func_code':25s} | {'module_code':20s} | {'order':5s} | {'功能名稱':20s}")
        print("-" * 80)

        for row in result:
            id_val, func_code, func_cname, module_code, func_order, is_mana = row
            mana_mark = "[管]" if is_mana else "   "
            module_str = module_code or "NULL"
            print(f"{id_val:3d} | {func_code:25s} | {module_str:20s} | {func_order:5d} | {func_cname:20s} {mana_mark}")

        print("-" * 80)
        print(f"總計: {len(result)} 筆資料")


if __name__ == "__main__":
    print("="*80)
    print("system_functions 資料表備份工具")
    print("="*80)

    # 先顯示目前的資料
    show_current_data()

    # 執行備份
    print("\n" + "="*80)
    backup_system_functions()
    print("="*80)
