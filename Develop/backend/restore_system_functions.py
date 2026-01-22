"""
還原 system_functions 資料表
使用 Python，不需要懂 PostgreSQL 指令
"""

from sqlalchemy import create_engine, text
from app.core.config import settings


def restore_system_functions():
    """從 SQL 檔案還原 system_functions"""
    engine = create_engine(settings.DATABASE_URL)

    print("正在還原 system_functions 資料表...")

    backup_file = "../../系統設計/應用系統設計/應用系統基礎功能清冊.SQL"

    try:
        # 讀取 SQL 檔案
        with open(backup_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print(f"已讀取備份檔案: {backup_file}")

        with engine.connect() as conn:
            # 詢問是否要清空現有資料
            confirm = input("\n警告：這將清空現有的 system_functions 資料！\n確定要繼續嗎？(yes/no): ")

            if confirm.lower() != 'yes':
                print("已取消還原")
                return

            print("\n正在清空現有資料...")
            conn.execute(text("TRUNCATE system_functions RESTART IDENTITY CASCADE"))
            conn.commit()
            print("已清空")

            print("\n正在匯入資料...")
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
                    if statement.strip():
                        statements.append(statement)
                    current_statement = []

            # 執行每個語句
            for statement in statements:
                try:
                    conn.execute(text(statement))
                except Exception as e:
                    print(f"執行語句時發生錯誤: {str(e)}")
                    print(f"語句: {statement[:100]}...")
                    raise

            conn.commit()
            print("資料匯入完成")

            # 驗證結果
            print("\n驗證結果:")
            result = conn.execute(text("SELECT COUNT(*) FROM system_functions")).scalar()
            print(f"共匯入 {result} 筆資料")

            # 顯示前 5 筆
            print("\n前 5 筆資料:")
            rows = conn.execute(text('''
                SELECT id, func_code, func_cname
                FROM system_functions
                ORDER BY id
                LIMIT 5
            ''')).fetchall()

            for row in rows:
                print(f"  ID {row[0]:2d}: {row[1]:25s} - {row[2]}")

            print("\n還原完成！")

    except FileNotFoundError:
        print(f"錯誤：找不到備份檔案 {backup_file}")
    except Exception as e:
        print(f"錯誤：{str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*80)
    print("system_functions 資料表還原工具")
    print("="*80)
    restore_system_functions()
    print("="*80)
