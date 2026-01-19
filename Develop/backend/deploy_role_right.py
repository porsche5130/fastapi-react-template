"""
角色權限設定作業 - 部署腳本
執行資料庫建表與功能新增
"""

import sys
import io
import psycopg2
from app.core.config import settings

# 設定 stdout 編碼為 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def deploy_role_right():
    """部署角色權限功能"""
    print("=" * 60)
    print("角色權限設定作業 - 部署開始")
    print("=" * 60)

    # 解析資料庫 URL
    # DATABASE_URL 格式: postgresql://user:password@host:port/dbname
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")

    try:
        # 連接資料庫
        print("\n[1/3] 連接資料庫...")
        conn = psycopg2.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        print("[OK] 資料庫連接成功")

        # 建立 role_right 資料表
        print("\n[2/3] 建立 role_right 資料表...")
        with open('create_role_right_table.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
            cursor.execute(sql)
            conn.commit()
        print("[OK] role_right 資料表建立成功")

        # 新增功能至系統功能表
        print("\n[3/3] 新增功能至系統功能表...")
        with open('insert_role_right_function.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
            cursor.execute(sql)
            conn.commit()
        print("[OK] 功能新增成功")

        # 關閉連接
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("[OK] 角色權限設定作業部署完成")
        print("=" * 60)
        print("\n下一步:")
        print("1. 執行測試: pytest tests/test_role_right.py -v")
        print("2. 啟動後端: python -m uvicorn app.main:app --reload")
        print("3. 啟動前端: cd ../frontend && npm start")
        print()

        return True

    except Exception as e:
        print(f"\n[ERROR] 部署失敗: {str(e)}")
        return False


if __name__ == "__main__":
    deploy_role_right()
