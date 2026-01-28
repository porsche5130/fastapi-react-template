"""
List Users from Database
列出資料庫中的使用者
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.user import User

def list_users():
    """List all users"""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).limit(10).all()

        print("=" * 60)
        print("Active Users in Database")
        print("=" * 60)

        if not users:
            print("No active users found")
            return

        for user in users:
            print(f"\nUser ID: {user.id}")
            print(f"  Account: {user.account}")
            print(f"  Username: {user.username}")
            print(f"  Organization ID: {user.organization_id}")
            print(f"  Is Active: {user.is_active}")
            print(f"  Created: {user.created_at}")

        print("\n" + "=" * 60)
        print(f"Total active users: {len(users)}")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
