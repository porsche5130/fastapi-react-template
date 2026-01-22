"""
執行資料表遷移
將舊資料表改名為新的標準化命名
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
import sys


def run_migration():
    """執行資料表遷移"""
    engine = create_engine(settings.DATABASE_URL)

    print("=" * 100)
    print("資料表遷移工具 - 先建後拆策略")
    print("=" * 100)

    try:
        with engine.connect() as conn:
            # 步驟 1: 建立新資料表
            print("\n步驟 1/3: 建立新資料表...")
            print("-" * 100)

            with open("migrations/04_create_new_tables.sql", 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # 分割並執行 SQL 語句
            statements = []
            current_statement = []

            for line in sql_content.split('\n'):
                line = line.strip()
                # 跳過註解和空行
                if not line or line.startswith('--'):
                    continue

                current_statement.append(line)

                # 如果遇到分號，表示一個語句結束
                if line.endswith(';'):
                    statement = ' '.join(current_statement)
                    if statement.strip() and not statement.strip().startswith('--'):
                        statements.append(statement)
                    current_statement = []

            for i, statement in enumerate(statements, 1):
                try:
                    conn.execute(text(statement))
                    print(f"  [{i}/{len(statements)}] 執行成功")
                except Exception as e:
                    print(f"  [{i}/{len(statements)}] 執行失敗: {str(e)}")
                    print(f"  SQL: {statement[:100]}...")
                    raise

            conn.commit()
            print("\n[SUCCESS] 新資料表建立完成")

            # 步驟 2: 遷移資料
            print("\n步驟 2/3: 遷移資料...")
            print("-" * 100)

            # 詢問是否要遷移資料
            confirm = input("\n是否要將舊資料遷移到新資料表？(yes/no): ")
            if confirm.lower() != 'yes':
                print("已取消資料遷移")
                print("\n注意：")
                print("  - 新資料表已建立")
                print("  - 但尚未遷移資料")
                print("  - 您可以稍後執行 migrations/05_migrate_data_to_new_tables.sql")
                return

            with open("migrations/05_migrate_data_to_new_tables.sql", 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # 分割並執行 SQL 語句
            statements = []
            current_statement = []

            for line in sql_content.split('\n'):
                line = line.strip()
                if not line or line.startswith('--'):
                    continue

                current_statement.append(line)

                if line.endswith(';'):
                    statement = ' '.join(current_statement)
                    if statement.strip() and not statement.strip().startswith('--'):
                        statements.append(statement)
                    current_statement = []

            for i, statement in enumerate(statements, 1):
                try:
                    result = conn.execute(text(statement))
                    # 如果是 SELECT 語句，顯示結果
                    if statement.strip().upper().startswith('SELECT'):
                        rows = result.fetchall()
                        if rows:
                            print(f"\n  [{i}/{len(statements)}] 查詢結果:")
                            for row in rows:
                                print(f"    {row}")
                    else:
                        print(f"  [{i}/{len(statements)}] 執行成功")
                except Exception as e:
                    print(f"  [{i}/{len(statements)}] 執行失敗: {str(e)}")
                    print(f"  SQL: {statement[:100]}...")
                    # 資料遷移失敗不一定要中斷（可能是資料已存在）
                    if "duplicate key" not in str(e).lower():
                        raise

            conn.commit()
            print("\n[SUCCESS] 資料遷移完成")

            # 步驟 3: 驗證結果
            print("\n步驟 3/3: 驗證結果...")
            print("-" * 100)

            # 檢查新資料表的筆數
            tables = [
                ('user_role', 'user_roles'),
                ('role_right', 'role_rights'),
                ('userlogs', 'user_logs')
            ]

            print("\n資料表遷移結果:")
            print(f"{'舊表名稱':20} {'舊表筆數':>10} {'新表名稱':20} {'新表筆數':>10} {'狀態':>10}")
            print("-" * 80)

            all_success = True
            for old_table, new_table in tables:
                try:
                    old_count = conn.execute(text(f"SELECT COUNT(*) FROM {old_table}")).scalar()
                    new_count = conn.execute(text(f"SELECT COUNT(*) FROM {new_table}")).scalar()

                    status = "[OK]" if old_count == new_count else "[WARNING]"
                    if old_count != new_count:
                        all_success = False

                    print(f"{old_table:20} {old_count:>10} {new_table:20} {new_count:>10} {status:>10}")
                except Exception as e:
                    print(f"{old_table:20} {'N/A':>10} {new_table:20} {'ERROR':>10} [FAIL]")
                    all_success = False

            print("-" * 80)

            if all_success:
                print("\n[SUCCESS] 所有資料遷移成功！")
                print("\n下一步:")
                print("  1. 重啟後端服務")
                print("  2. 測試新舊 API 端點是否都能正常運作")
                print("  3. 確認系統穩定運作至少一週後，執行 migrations/06_cleanup_old_tables.sql 清理舊資料表")
            else:
                print("\n[WARNING] 部分資料遷移可能有問題，請檢查上述報告")

    except Exception as e:
        print(f"\n[ERROR] 遷移失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 100)


if __name__ == "__main__":
    run_migration()
