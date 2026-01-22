"""
建立新版 Routes 檔案
從舊版 Routes 批次替換欄位名稱
"""

import os
import re
from pathlib import Path

# 設定檔案路徑
ROUTES_DIR = Path(__file__).parent / "app" / "routes"

# 定義檔案對應關係 (舊檔案, 新檔案, 替換規則)
FILE_MAPPINGS = [
    {
        "old_file": "userlog.py",
        "new_file": "user_logs.py",
        "replacements": [
            (r'from app\.models\.userlog import UserLog', 'from app.models.user_logs import UserLog'),
            (r'from app\.models\.sysfunction import SysFunction', 'from app.models.system_functions import SystemFunction'),
            (r'from app\.schemas\.userlog import', 'from app.schemas.user_logs import'),
            (r'\buser_detail_id\b', 'user_id'),
            (r'\bsysfunction_id\b', 'system_function_id'),
            (r'\bUserLog\.user_detail_id\b', 'UserLog.user_id'),
            (r'\bUserLog\.sysfunction_id\b', 'UserLog.system_function_id'),
            (r'description="作業人員ID"', 'description="使用者ID"'),
        ],
        "table_name": "userlogs",
        "new_table_name": "user_logs"
    },
    {
        "old_file": "user_role.py",
        "new_file": "user_roles.py",
        "replacements": [
            (r'from app\.models\.user_role import UserRole', 'from app.models.user_roles import UserRole'),
            (r'from app\.schemas\.user_role import', 'from app.schemas.user_roles import'),
            (r'__tablename__ = "user_role"', '__tablename__ = "user_roles"'),
        ],
        "table_name": "user_role",
        "new_table_name": "user_roles"
    },
    {
        "old_file": "role_right.py",
        "new_file": "role_rights.py",
        "replacements": [
            (r'from app\.models\.role_right import RoleRight', 'from app.models.role_rights import RoleRight'),
            (r'from app\.models\.user_role import UserRole', 'from app.models.user_roles import UserRole'),
            (r'from app\.models\.sysfunction import SysFunction', 'from app.models.system_functions import SystemFunction'),
            (r'from app\.schemas\.role_right import', 'from app.schemas.role_rights import'),
            (r'\bsysfunction_id\b', 'system_function_id'),
            (r'\bRoleRight\.sysfunction_id\b', 'RoleRight.system_function_id'),
            (r'__tablename__ = "role_right"', '__tablename__ = "role_rights"'),
        ],
        "table_name": "role_right",
        "new_table_name": "role_rights"
    }
]


def process_file(mapping: dict) -> bool:
    """處理單一檔案的替換"""
    old_path = ROUTES_DIR / mapping["old_file"]
    new_path = ROUTES_DIR / mapping["new_file"]

    if not old_path.exists():
        print(f"[FAIL] 來源檔案不存在: {old_path}")
        return False

    print(f"\n處理檔案: {mapping['old_file']} → {mapping['new_file']}")

    try:
        # 讀取來源檔案
        with open(old_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 執行所有替換
        for pattern, replacement in mapping["replacements"]:
            old_content = content
            content = re.sub(pattern, replacement, content)
            if old_content != content:
                print(f"  [OK] 替換: {pattern}")

        # 寫入新檔案
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[SUCCESS] 成功建立: {new_path}")
        return True

    except Exception as e:
        print(f"[ERROR] 處理失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主程序"""
    print("=" * 80)
    print("建立新版 Routes 檔案")
    print("=" * 80)

    success_count = 0
    fail_count = 0

    for mapping in FILE_MAPPINGS:
        if process_file(mapping):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 80)
    print(f"處理完成: 成功 {success_count} 個，失敗 {fail_count} 個")
    print("=" * 80)


if __name__ == "__main__":
    main()
