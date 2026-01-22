"""
建立 system_codes 資料表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def create_systemcode_table():
    """建立 system_codes 資料表"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # 建立資料表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS system_codes (
                id SERIAL PRIMARY KEY,
                code_etype VARCHAR(100) NOT NULL,
                code_ctype VARCHAR(200) NOT NULL,
                code VARCHAR(50) NOT NULL,
                code_cname VARCHAR(300) NOT NULL,
                code_ename VARCHAR(300),
                "order" INTEGER NOT NULL DEFAULT 0,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                note1 VARCHAR(500),
                note2 VARCHAR(500),
                note3 VARCHAR(500),
                note4 VARCHAR(500),
                note5 VARCHAR(500),
                edit_by INTEGER NOT NULL REFERENCES user_detail(id),
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # 建立索引
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_system_codes_type ON system_codes(code_etype, code_ctype);
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_system_codes_code ON system_codes(code);
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_system_codes_active ON system_codes(is_active);
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_system_codes_order ON system_codes("order");
        """))

        conn.commit()
        print("[OK] system_codes table created successfully")


def add_sysfunction_entry():
    """在 sysfunction 中新增 system_codes 功能"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # 檢查是否已存在
        result = conn.execute(text("""
            SELECT id FROM sysfunction WHERE func_code = 'system_codes'
        """))

        if result.fetchone():
            print("[WARN]  system_codes 功能已存在於 sysfunction")
            return

        # 取得 system 節點的 ID
        result = conn.execute(text("""
            SELECT id FROM sysfunction WHERE func_code = 'system' AND func_type = 1
        """))
        parent_row = result.fetchone()

        if not parent_row:
            print("[ERROR] 找不到 system 節點")
            return

        parent_id = parent_row[0]

        # 取得最大的 func_order
        result = conn.execute(text("""
            SELECT COALESCE(MAX(func_order), 0) FROM sysfunction WHERE parent_id = :parent_id
        """), {"parent_id": parent_id})
        max_order = result.fetchone()[0]

        # 新增功能
        # 注意：func_code 用於前端路由，func_module_name 用於後端 API 路由和資料表名稱
        conn.execute(text("""
            INSERT INTO sysfunction (
                func_code, func_cname, func_ename, func_type, parent_id,
                func_order, func_icon, func_module_name, is_mana, is_active,
                is_create, is_read, is_update, is_delete, is_print, is_file,
                memo, edit_by, created_at
            ) VALUES (
                'system_codes', '系統代碼設定', 'System Codes', 2, :parent_id,
                :func_order, 'settings', 'system_codes', TRUE, TRUE,
                TRUE, TRUE, TRUE, TRUE, FALSE, FALSE,
                '系統代碼明細檔管理', 1, CURRENT_TIMESTAMP
            )
        """), {"parent_id": parent_id, "func_order": max_order + 1})

        conn.commit()
        print("[OK] system_codes 功能已新增至 sysfunction")


if __name__ == "__main__":
    print("開始建立 system_codes 資料表...")
    create_systemcode_table()

    print("\n新增 sysfunction 功能項目...")
    add_sysfunction_entry()

    print("\n[OK] 完成！")
