# -*- coding: utf-8 -*-
"""
PostgreSQL 連線檢查工具
"""
import psycopg2

print("PostgreSQL Connection Checker")
print("=" * 60)

# 測試不同的連線配置
test_configs = [
    {
        "desc": "dev/dev123",
        "params": {
            "host": "localhost",
            "port": 5432,
            "database": "pa64_dev",
            "user": "dev",
            "password": "dev123"
        }
    },
    {
        "desc": "postgres/postgres",
        "params": {
            "host": "localhost",
            "port": 5432,
            "database": "postgres",
            "user": "postgres",
            "password": "postgres"
        }
    },
    {
        "desc": "postgres (no password)",
        "params": {
            "host": "localhost",
            "port": 5432,
            "database": "postgres",
            "user": "postgres",
            "password": ""
        }
    },
]

for test in test_configs:
    print(f"\nTrying: {test['desc']}")
    try:
        conn = psycopg2.connect(**test['params'], connect_timeout=3)
        cur = conn.cursor()

        # 取得版本
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]

        # 列出所有資料庫
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
        databases = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        print(f"  SUCCESS!")
        print(f"  PostgreSQL: {version.split(',')[0]}")
        print(f"  Databases: {', '.join(databases)}")

        print("\n" + "=" * 60)
        print("Connection successful!")
        print("=" * 60)

        params = test['params']
        print(f"\nConnection info:")
        print(f"  Host: {params['host']}")
        print(f"  Port: {params['port']}")
        print(f"  Database: {params['database']}")
        print(f"  User: {params['user']}")
        print(f"  Password: {params['password']}")

        print(f"\nConnection string:")
        print(f"  postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}")

        print(f"\nFor Docker:")
        print(f"  postgresql://{params['user']}:{params['password']}@host.docker.internal:{params['port']}/{params['database']}")

        # 如果連線的不是 pa64_dev，提示建立資料庫
        if 'pa64_dev' in databases:
            print(f"\n✓ Database 'pa64_dev' exists!")
        else:
            print(f"\n! Database 'pa64_dev' does NOT exist")
            print(f"  Please create it:")
            print(f"    psql -U {params['user']} -c 'CREATE DATABASE pa64_dev;'")

        print()
        break

    except psycopg2.OperationalError as e:
        print(f"  FAILED: {e}")
    except Exception as e:
        print(f"  ERROR: {e}")

else:
    print("\n" + "=" * 60)
    print("Could not connect with any configuration")
    print("=" * 60)
    print("\nPlease provide:")
    print("1. PostgreSQL host (default: localhost)")
    print("2. PostgreSQL port (default: 5432)")
    print("3. PostgreSQL user")
    print("4. PostgreSQL password")
    print("5. Database name")
