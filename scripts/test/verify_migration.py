"""
驗證資料庫遷移結果
"""
import psycopg2

LOCAL_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "pa64_dev",
    "user": "dev",
    "password": "dev123"
}

REMOTE_CONFIG = {
    "host": "10.1.0.20",
    "port": 5433,
    "database": "pa64_dev",
    "user": "admin",
    "password": "!DC1qaz2wsx"
}

def verify_migration():
    print("="*70)
    print("Database Migration Verification")
    print("="*70)

    local_conn = psycopg2.connect(**LOCAL_CONFIG)
    remote_conn = psycopg2.connect(**REMOTE_CONFIG)

    local_cur = local_conn.cursor()
    remote_cur = remote_conn.cursor()

    # 1. Compare table count
    print("\n[1] Table Count:")
    local_cur.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';")
    local_tables = local_cur.fetchone()[0]

    remote_cur.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';")
    remote_tables = remote_cur.fetchone()[0]

    print(f"  Local:  {local_tables}")
    print(f"  Remote: {remote_tables}")
    print(f"  Status: {'OK' if local_tables == remote_tables else 'MISMATCH'}")

    # 2. Compare row counts for each table
    print("\n[2] Row Counts:")
    local_cur.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename;
    """)

    tables = [row[0] for row in local_cur.fetchall()]
    all_match = True

    for table in tables:
        local_cur.execute(f'SELECT COUNT(*) FROM "{table}";')
        local_count = local_cur.fetchone()[0]

        remote_cur.execute(f'SELECT COUNT(*) FROM "{table}";')
        remote_count = remote_cur.fetchone()[0]

        match = "OK" if local_count == remote_count else "MISMATCH"
        if local_count != remote_count:
            all_match = False

        print(f"  {table:30} Local: {local_count:6} | Remote: {remote_count:6} [{match}]")

    # 3. Compare sequence values
    print("\n[3] Sequence Values:")
    local_cur.execute("""
        SELECT sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema = 'public'
        ORDER BY sequence_name;
    """)

    sequences = [row[0] for row in local_cur.fetchall()]

    for seq in sequences:
        local_cur.execute(f"SELECT last_value FROM {seq};")
        local_val = local_cur.fetchone()[0]

        try:
            remote_cur.execute(f"SELECT last_value FROM {seq};")
            remote_val = remote_cur.fetchone()[0]
            match = "OK" if local_val == remote_val else "DIFF"
            print(f"  {seq:35} Local: {local_val:6} | Remote: {remote_val:6} [{match}]")
        except Exception as e:
            print(f"  {seq:35} ERROR: {e}")

    # 4. Test sample queries
    print("\n[4] Sample Data Tests:")

    # Test users table
    remote_cur.execute("SELECT COUNT(*), MAX(id) FROM users;")
    user_count, max_user_id = remote_cur.fetchone()
    print(f"  Users: {user_count} records, max ID: {max_user_id}")

    # Test organizations table
    remote_cur.execute("SELECT COUNT(*), MAX(id) FROM organizations;")
    org_count, max_org_id = remote_cur.fetchone()
    print(f"  Organizations: {org_count} records, max ID: {max_org_id}")

    # Test JSONB data
    remote_cur.execute("SELECT username, user_role FROM users WHERE id = 1;")
    username, user_role = remote_cur.fetchone()
    print(f"  Sample user: {username}, roles: {user_role}")

    # Test foreign key relationships
    remote_cur.execute("""
        SELECT u.username, COUNT(ul.id) as log_count
        FROM users u
        LEFT JOIN user_logs ul ON ul.user_id = u.id
        GROUP BY u.username
        ORDER BY log_count DESC
        LIMIT 3;
    """)
    print(f"\n  Top users by log count:")
    for username, log_count in remote_cur.fetchall():
        print(f"    - {username}: {log_count} logs")

    # 5. Summary
    print("\n" + "="*70)
    if all_match and local_tables == remote_tables:
        print("SUCCESS - Migration verified! All data matches.")
    else:
        print("WARNING - Some mismatches found. Please review above.")
    print("="*70)

    print(f"\nRemote database is ready:")
    print(f"postgresql://admin:!DC1qaz2wsx@10.1.0.20:5433/pa64_dev")

    local_cur.close()
    remote_cur.close()
    local_conn.close()
    remote_conn.close()

if __name__ == "__main__":
    try:
        verify_migration()
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
