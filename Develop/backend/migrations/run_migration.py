"""
資料庫遷移執行腳本
執行 sysfunction → system_functions 的遷移
"""

import sys
import os
from pathlib import Path

# 設定 Windows 控制台編碼為 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.core.database import engine


def run_sql_file(filename: str) -> bool:
    """執行 SQL 檔案"""
    sql_file = Path(__file__).parent / filename

    if not sql_file.exists():
        print(f"[ERROR] 找不到檔案: {sql_file}")
        return False

    print(f"\n{'='*60}")
    print(f"執行: {filename}")
    print(f"{'='*60}\n")

    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        with engine.connect() as conn:
            # 使用 text() 包裝 SQL，並設定 execution_options
            conn.execute(text(sql))
            conn.commit()

        print(f"[SUCCESS] {filename} 執行成功！\n")
        return True

    except Exception as e:
        print(f"[ERROR] {filename} 執行失敗: {str(e)}\n")
        return False


def verify_migration() -> bool:
    """驗證遷移結果"""
    print(f"\n{'='*60}")
    print("驗證遷移結果")
    print(f"{'='*60}\n")

    try:
        with engine.connect() as conn:
            # 檢查新表是否存在
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename IN ('sysfunction', 'system_functions')
                ORDER BY tablename;
            """))
            tables = [row[0] for row in result]

            print("[INFO] 現有資料表:")
            for table in tables:
                print(f"  - {table}")

            if 'system_functions' not in tables:
                print("\n[ERROR] 新表 system_functions 不存在！")
                return False

            # 檢查資料數量
            result = conn.execute(text("SELECT COUNT(*) FROM system_functions;"))
            new_count = result.scalar()

            if 'sysfunction' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM sysfunction;"))
                old_count = result.scalar()
                print(f"\n[INFO] 資料數量:")
                print(f"  - sysfunction: {old_count} 筆")
                print(f"  - system_functions: {new_count} 筆")

                if old_count != new_count:
                    print(f"\n[WARNING] 警告: 資料數量不一致！")
                    return False
            else:
                print(f"\n[INFO] 資料數量:")
                print(f"  - system_functions: {new_count} 筆")

            # 檢查 module_code 欄位
            result = conn.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'system_functions'
                AND column_name = 'module_code';
            """))
            col = result.fetchone()

            if not col:
                print("\n[ERROR] module_code 欄位不存在！")
                return False

            print(f"\n[SUCCESS] module_code 欄位: {col[1]}")

            # 檢查 system_functions 記錄
            result = conn.execute(text("""
                SELECT id, func_code, module_code, func_cname
                FROM system_functions
                WHERE func_code = 'system_functions'
                LIMIT 1;
            """))
            record = result.fetchone()

            if record:
                print(f"\n[SUCCESS] system_functions 記錄已更新:")
                print(f"  - ID: {record[0]}")
                print(f"  - func_code: {record[1]}")
                print(f"  - module_code: {record[2]}")
                print(f"  - func_cname: {record[3]}")
            else:
                print(f"\n[WARNING] 警告: 找不到 system_functions 記錄")

            print("\n[SUCCESS] 驗證通過！")
            return True

    except Exception as e:
        print(f"\n[ERROR] 驗證失敗: {str(e)}")
        return False


def main():
    """主程式"""
    print("\n" + "="*60)
    print("資料庫遷移：sysfunction → system_functions")
    print("="*60)

    # 詢問確認
    print("\n[WARNING] 重要提醒:")
    print("1. 執行前請確保已備份資料庫")
    print("2. 此操作會建立新表 system_functions")
    print("3. 舊表 sysfunction 會保留")
    print("4. 資料會從舊表複製到新表")

    response = input("\n是否繼續? (yes/no): ").lower()
    if response not in ['yes', 'y']:
        print("\n[CANCELLED] 取消執行")
        return

    # 執行遷移腳本
    success = True

    # 步驟 1: 建立新表
    if not run_sql_file('01_create_system_functions_table.sql'):
        success = False
        print("\n[ERROR] 遷移失敗: 無法建立新表")
        return

    # 步驟 2: 遷移資料
    if not run_sql_file('02_migrate_data_to_system_functions.sql'):
        success = False
        print("\n[ERROR] 遷移失敗: 無法遷移資料")
        return

    # 驗證結果
    if not verify_migration():
        success = False
        print("\n[ERROR] 遷移失敗: 驗證不通過")
        return

    if success:
        print("\n" + "="*60)
        print("[SUCCESS] 遷移完成！")
        print("="*60)
        print("\n下一步:")
        print("1. 更新後端程式碼（已完成）")
        print("2. 更新前端程式碼（已完成）")
        print("3. 測試新系統功能")
        print("4. 確認穩定後執行 03_cleanup_old_sysfunction.sql")
        print("\n[INFO] 詳細說明請參考: migrations/README.md")


if __name__ == "__main__":
    main()
