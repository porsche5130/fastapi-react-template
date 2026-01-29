"""
資料庫初始化腳本
自動建立資料表並填入初始資料
"""
import sys
from pathlib import Path

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent / "Develop" / "backend"
sys.path.insert(0, str(project_root))

def main():
    print("="*80)
    print("PA6.4 資料庫初始化工具")
    print("="*80)

    # 步驟 1: 檢查環境
    print("\n[步驟 1/5] 檢查環境...")
    try:
        from app.core.database import engine, Base
        from sqlalchemy import text, inspect
        print("  ✓ 成功載入資料庫模組")
    except Exception as e:
        print(f"  ✗ 錯誤: {e}")
        print("\n請確認:")
        print("  1. 已安裝所有依賴: pip install -r requirements.txt")
        print("  2. 已設定 .env 檔案")
        return False

    # 步驟 2: 測試資料庫連線
    print("\n[步驟 2/5] 測試資料庫連線...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"  ✓ PostgreSQL 版本: {version.split(',')[0]}")
    except Exception as e:
        print(f"  ✗ 無法連接資料庫: {e}")
        print("\n請檢查 .env 中的 DATABASE_URL 設定")
        return False

    # 步驟 3: 檢查資料表是否已存在
    print("\n[步驟 3/5] 檢查現有資料表...")
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if existing_tables:
        print(f"  ! 發現 {len(existing_tables)} 個現有資料表:")
        for table in sorted(existing_tables):
            print(f"    - {table}")

        print("\n  警告: 資料庫不是空的！")
        response = input("  是否要繼續? 可能會覆蓋現有資料 (yes/no): ").strip().lower()

        if response != 'yes':
            print("  取消初始化")
            return False
    else:
        print("  ✓ 資料庫是空的，可以安全初始化")

    # 步驟 4: 建立所有資料表
    print("\n[步驟 4/5] 建立資料表結構...")
    try:
        # 匯入所有 models 以確保它們被註冊
        from app import models

        # 建立所有資料表
        Base.metadata.create_all(bind=engine)

        # 驗證建立結果
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        print(f"  ✓ 成功建立 {len(new_tables)} 個資料表:")
        for table in sorted(new_tables):
            print(f"    - {table}")

    except Exception as e:
        print(f"  ✗ 建立資料表失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 步驟 5: 建議後續步驟
    print("\n[步驟 5/5] 初始化完成")
    print("\n" + "="*80)
    print("SUCCESS! 資料表結構已建立完成")
    print("="*80)

    print("\n後續步驟:")
    print("  1. 執行 Migration 腳本填入初始資料:")
    print("     cd Develop/backend/migrations")
    print("     python run_migration_auto.py")
    print()
    print("  2. 或手動建立初始資料:")
    print("     - 組織資料 (organizations)")
    print("     - 管理員帳號 (users)")
    print("     - 角色權限 (user_roles, role_rights)")
    print("     - 系統功能 (system_functions)")
    print("     - 系統設定 (sys_profiles)")
    print()
    print("  3. 啟動應用程式:")
    print("     python -m uvicorn app.main:app --reload")
    print()
    print("詳細說明請參考: Develop/docs/DATABASE_INITIALIZATION_GUIDE.md")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n使用者取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
