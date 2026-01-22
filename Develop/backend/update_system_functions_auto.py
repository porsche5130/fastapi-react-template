"""
自動更新 system_functions 資料表
"""
from sqlalchemy import create_engine, text
from app.core.config import settings


def update_system_functions():
    """更新 system_functions"""
    engine = create_engine(settings.DATABASE_URL)

    print("Updating system_functions...")

    backup_file = "../../系統設計/應用系統設計/應用系統基礎功能清冊.SQL"

    try:
        # 讀取 SQL 檔案
        with open(backup_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print(f"Loaded backup file: {backup_file}")

        with engine.connect() as conn:
            print("\nClearing existing data...")
            conn.execute(text("TRUNCATE system_functions RESTART IDENTITY CASCADE"))
            conn.commit()
            print("[OK] Cleared")

            print("\nImporting data...")
            # 分割 SQL 語句並執行（跳過註解）
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
                    if statement.strip() and not statement.strip().startswith('SELECT'):
                        statements.append(statement)
                    current_statement = []

            # 執行每個語句
            for statement in statements:
                try:
                    conn.execute(text(statement))
                except Exception as e:
                    if 'SELECT' not in statement.upper():
                        print(f"[ERROR] Error executing statement: {str(e)}")
                        print(f"Statement: {statement[:100]}...")

            conn.commit()
            print("[OK] Data imported")

            # 驗證結果
            print("\nVerification:")
            result = conn.execute(text("SELECT COUNT(*) FROM system_functions")).scalar()
            print(f"  Total records: {result}")

            # 顯示前 5 筆
            print("\nFirst 5 records:")
            rows = conn.execute(text('''
                SELECT id, func_code, func_cname, module_code
                FROM system_functions
                ORDER BY id
                LIMIT 5
            ''')).fetchall()

            for row in rows:
                print(f"  ID {row[0]:2d}: {row[1]:25s} - {row[2]:20s} ({row[3]})")

            # 檢查 dashboard 是否已改為 home
            print("\nChecking dashboard -> home migration:")
            row = conn.execute(text('''
                SELECT id, func_code, module_code, func_cname
                FROM system_functions
                WHERE func_code = 'dashboard'
            ''')).fetchone()

            if row:
                print(f"  ID: {row[0]}, func_code: {row[1]}, module_code: {row[2]}, cname: {row[3]}")
                if row[2] == 'home':
                    print("  [OK] dashboard module_code is now 'home'")
                else:
                    print(f"  [WARNING] dashboard module_code is '{row[2]}', expected 'home'")

            print("\n[SUCCESS] system_functions updated!")

    except FileNotFoundError:
        print(f"[ERROR] File not found: {backup_file}")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 80)
    print("system_functions Auto Update Tool")
    print("=" * 80)
    update_system_functions()
    print("=" * 80)
