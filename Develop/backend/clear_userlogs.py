"""
清除 userlogs 資料表並重置自動編號
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

with engine.connect() as conn:
    trans = conn.begin()

    try:
        # 1. 刪除所有資料
        print("步驟 1: 刪除 userlogs 所有資料...")
        result = conn.execute(text("DELETE FROM userlogs;"))
        deleted_count = result.rowcount
        print(f"[OK] 已刪除 {deleted_count} 筆資料")

        # 2. 重置自動編號序列
        print("\n步驟 2: 重置自動編號序列...")
        conn.execute(text("ALTER SEQUENCE userlogs_id_seq RESTART WITH 1;"))
        print("[OK] 自動編號已重置為 1")

        # 3. 驗證
        print("\n步驟 3: 驗證...")
        result = conn.execute(text("SELECT COUNT(*) FROM userlogs;"))
        count = result.scalar()
        print(f"[OK] 當前資料筆數: {count}")

        result = conn.execute(text("SELECT last_value FROM userlogs_id_seq;"))
        next_id = result.scalar()
        print(f"[OK] 下一個 ID 將會是: {next_id}")

        trans.commit()
        print("\n[SUCCESS] userlogs 已清空，自動編號已重置！")

    except Exception as e:
        trans.rollback()
        print(f"\n[ERROR] {e}")
        raise
