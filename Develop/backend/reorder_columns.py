"""
重新排序 sysfunction 資料表的欄位順序
警告：此操作會重建資料表，請先備份資料！
"""
import sys
import os
import io

# 設定 stdout 編碼為 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def reorder_sysfunction_columns():
    """重新排序 sysfunction 資料表的欄位"""

    engine = create_engine(str(settings.DATABASE_URL))

    print("警告：此操作將重建 sysfunction 資料表！")
    print("請確保已備份資料庫。")
    response = input("是否繼續？(yes/no): ")

    if response.lower() != 'yes':
        print("操作已取消。")
        return

    with engine.connect() as conn:
        trans = conn.begin()

        try:
            print("\n步驟 1: 創建新表結構...")
            conn.execute(text("""
                CREATE TABLE sysfunction_new (
                    id SERIAL PRIMARY KEY,
                    func_code VARCHAR(200) NOT NULL,
                    func_cname VARCHAR(200) NOT NULL,
                    func_ename VARCHAR(200) NOT NULL,
                    upper_func_id INTEGER NOT NULL DEFAULT 0,
                    func_type INTEGER NOT NULL,
                    func_order INTEGER NOT NULL,
                    func_icon VARCHAR(200),
                    func_module_name VARCHAR(200),
                    module_item JSONB NOT NULL DEFAULT '[]'::jsonb,
                    description TEXT,
                    is_mana BOOLEAN NOT NULL DEFAULT FALSE,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    edit_by INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            print("   [OK] 新表已創建")

            print("\n步驟 2: 複製資料...")
            result = conn.execute(text("""
                INSERT INTO sysfunction_new
                    (id, func_code, func_cname, func_ename, upper_func_id,
                     func_type, func_order, func_icon, func_module_name,
                     module_item, description, is_mana, is_active,
                     edit_by, created_at, updated_at)
                SELECT
                    id, func_code, func_cname, func_ename, upper_func_id,
                    func_type, func_order, func_icon, func_module_name,
                    module_item, description, is_mana, is_active,
                    edit_by, created_at, updated_at
                FROM sysfunction
            """))
            print(f"   [OK] 已複製 {result.rowcount} 筆資料")

            print("\n步驟 3: 刪除舊表...")
            conn.execute(text("DROP TABLE sysfunction CASCADE"))
            print("   [OK] 舊表已刪除")

            print("\n步驟 4: 重新命名新表...")
            conn.execute(text("ALTER TABLE sysfunction_new RENAME TO sysfunction"))
            print("   [OK] 表已重新命名")

            print("\n步驟 5: 重建索引...")
            conn.execute(text("CREATE INDEX idx_sysfunction_code ON sysfunction(func_code)"))
            conn.execute(text("CREATE INDEX idx_sysfunction_upper ON sysfunction(upper_func_id)"))
            conn.execute(text("CREATE INDEX idx_sysfunction_type ON sysfunction(func_type)"))
            conn.execute(text("CREATE INDEX idx_sysfunction_active ON sysfunction(is_active)"))
            conn.execute(text("CREATE INDEX idx_sysfunction_order ON sysfunction(func_order)"))
            print("   [OK] 索引已重建")

            print("\n步驟 6: 重建約束...")
            conn.execute(text("""
                ALTER TABLE sysfunction
                ADD CONSTRAINT chk_func_type CHECK (func_type IN (1, 2))
            """))
            conn.execute(text("""
                ALTER TABLE sysfunction
                ADD CONSTRAINT chk_func_module
                CHECK (
                    (func_type = 1 AND func_module_name IS NULL) OR
                    (func_type = 2 AND func_module_name IS NOT NULL)
                )
            """))
            print("   [OK] 約束已重建")

            print("\n步驟 7: 重建外鍵...")
            conn.execute(text("""
                ALTER TABLE sysfunction
                ADD CONSTRAINT fk_sysfunction_editor
                FOREIGN KEY (edit_by) REFERENCES user_detail(id)
            """))
            print("   [OK] 外鍵已重建")

            print("\n步驟 8: 重置序列...")
            conn.execute(text("""
                SELECT setval('sysfunction_id_seq',
                    (SELECT MAX(id) FROM sysfunction), true)
            """))
            print("   [OK] 序列已重置")

            trans.commit()
            print("\n========================================")
            print("成功！資料表欄位順序已更新。")
            print("========================================")

        except Exception as e:
            trans.rollback()
            print(f"\n[錯誤] {e}")
            print("操作已回滾。")
            raise

if __name__ == "__main__":
    reorder_sysfunction_columns()
