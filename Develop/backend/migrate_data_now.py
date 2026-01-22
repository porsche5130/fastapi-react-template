"""
遷移資料到新資料表
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate_data():
    engine = create_engine(settings.DATABASE_URL)

    print("Start migrating data...")

    with engine.connect() as conn:
        # 1. 遷移 user_role → user_roles
        print("\n1. Migrating user_role -> user_roles...")
        result = conn.execute(text("""
            INSERT INTO user_roles (id, role_cname, role_ename, description, is_mana, is_active, edit_by, created_at, updated_at)
            SELECT id, role_cname, role_ename, description, is_mana, is_active, edit_by, created_at, updated_at
            FROM user_role
            ON CONFLICT (id) DO NOTHING
        """))
        print(f"   [OK] Migrated {result.rowcount} records")

        # 更新 sequence
        conn.execute(text("SELECT setval('user_roles_id_seq', (SELECT MAX(id) FROM user_roles))"))
        print("   [OK] Sequence updated")

        # 2. 遷移 role_right → role_rights
        print("\n2. Migrating role_right -> role_rights...")
        result = conn.execute(text("""
            INSERT INTO role_rights (
                id, user_role_id, system_function_id, func_code,
                is_create, is_read, is_update, is_delete, is_print, is_file,
                edit_by, created_at, updated_at
            )
            SELECT
                rr.id,
                rr.user_role_id,
                sf_new.id as system_function_id,
                rr.func_code,
                rr.is_create,
                rr.is_read,
                rr.is_update,
                rr.is_delete,
                rr.is_print,
                rr.is_file,
                rr.edit_by,
                rr.created_at,
                rr.updated_at
            FROM role_right rr
            INNER JOIN sysfunction sf_old ON rr.sysfunction_id = sf_old.id
            INNER JOIN system_functions sf_new ON sf_old.func_code = sf_new.func_code
            ON CONFLICT (id) DO NOTHING
        """))
        print(f"   [OK] Migrated {result.rowcount} records")

        # 更新 sequence
        conn.execute(text("SELECT setval('role_rights_id_seq', (SELECT MAX(id) FROM role_rights))"))
        print("   [OK] Sequence updated")

        # 3. 遷移 userlogs → user_logs
        print("\n3. Migrating userlogs -> user_logs...")
        result = conn.execute(text("""
            INSERT INTO user_logs (
                id, user_id, system_function_id, module_item, data_id, session_id,
                look_data, change_data, action_at, err_detail
            )
            SELECT
                ul.id,
                ul.user_detail_id as user_id,
                COALESCE(sf_new.id, 0) as system_function_id,
                ul.module_item,
                ul.data_id,
                ul.session_id,
                ul.look_data,
                ul.change_data,
                ul.action_at,
                ul.err_detail
            FROM userlogs ul
            LEFT JOIN sysfunction sf_old ON ul.sysfunction_id = sf_old.id
            LEFT JOIN system_functions sf_new ON sf_old.func_code = sf_new.func_code
            WHERE COALESCE(sf_new.id, 0) > 0
            ON CONFLICT (id) DO NOTHING
        """))
        print(f"   [OK] Migrated {result.rowcount} records")

        # 更新 sequence
        conn.execute(text("SELECT setval('user_logs_id_seq', (SELECT MAX(id) FROM user_logs))"))
        print("   [OK] Sequence updated")

        conn.commit()

        # 驗證結果
        print("\n" + "=" * 80)
        print("Migration Verification:")
        print("=" * 80)

        tables = [
            ('user_role', 'user_roles'),
            ('role_right', 'role_rights'),
            ('userlogs', 'user_logs')
        ]

        for old_table, new_table in tables:
            old_count = conn.execute(text(f"SELECT COUNT(*) FROM {old_table}")).scalar()
            new_count = conn.execute(text(f"SELECT COUNT(*) FROM {new_table}")).scalar()
            status = "[OK]" if old_count == new_count else "[WARNING]"
            print(f"{old_table:20} -> {new_table:20}  Old: {old_count:5}  New: {new_count:5}  {status}")

        print("=" * 80)
        print("\n[SUCCESS] Data migration completed!")

if __name__ == "__main__":
    migrate_data()
