"""
建立新資料表
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def create_tables():
    engine = create_engine(settings.DATABASE_URL)

    print("Start creating new tables...")

    with engine.connect() as conn:
        # 1. Create user_logs
        print("\n1. Creating user_logs table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                system_function_id INTEGER NOT NULL REFERENCES system_functions(id),
                module_item VARCHAR(50) NOT NULL CHECK (module_item IN ('Create', 'Read', 'Update', 'Delete', 'Print', 'File', 'Login')),
                data_id INTEGER,
                session_id VARCHAR(36),
                look_data JSONB NOT NULL DEFAULT '{}'::jsonb,
                change_data JSONB NOT NULL DEFAULT '{}'::jsonb,
                action_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                err_detail VARCHAR(2000)
            )
        """))
        print("   [OK] user_logs table created")

        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_logs_user ON user_logs(user_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_logs_function ON user_logs(system_function_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_logs_action_at ON user_logs(action_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_logs_module ON user_logs(module_item)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_logs_session ON user_logs(session_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_logs_data_id ON user_logs(data_id)"))
        print("   [OK] user_logs indexes created")

        # 2. Create user_roles
        print("\n2. Creating user_roles table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_roles (
                id SERIAL PRIMARY KEY,
                role_cname VARCHAR(200) NOT NULL,
                role_ename VARCHAR(200) NOT NULL,
                description TEXT,
                is_mana BOOLEAN NOT NULL DEFAULT FALSE,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                edit_by INTEGER NOT NULL REFERENCES users(id),
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))
        print("   [OK] user_roles table created")

        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_roles_active ON user_roles(is_active)"))
        print("   [OK] user_roles indexes created")

        # 3. Create role_rights
        print("\n3. Creating role_rights table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS role_rights (
                id SERIAL PRIMARY KEY,
                user_role_id INTEGER NOT NULL REFERENCES user_roles(id) ON DELETE CASCADE,
                system_function_id INTEGER NOT NULL REFERENCES system_functions(id) ON DELETE CASCADE,
                func_code VARCHAR(20) NOT NULL,
                is_create BOOLEAN NOT NULL DEFAULT FALSE,
                is_read BOOLEAN NOT NULL DEFAULT FALSE,
                is_update BOOLEAN NOT NULL DEFAULT FALSE,
                is_delete BOOLEAN NOT NULL DEFAULT FALSE,
                is_print BOOLEAN NOT NULL DEFAULT FALSE,
                is_file BOOLEAN NOT NULL DEFAULT FALSE,
                edit_by INTEGER NOT NULL REFERENCES users(id),
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))
        print("   [OK] role_rights table created")

        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_role_rights_role ON role_rights(user_role_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_role_rights_function ON role_rights(system_function_id)"))
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_role_rights_unique ON role_rights(user_role_id, system_function_id)"))
        print("   [OK] role_rights indexes created")

        conn.commit()

        print("\n[SUCCESS] All new tables created successfully!")

if __name__ == "__main__":
    create_tables()
