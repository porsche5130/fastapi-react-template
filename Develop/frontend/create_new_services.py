"""
建立新版前端服務檔案
從舊版服務批次替換 API 路徑
"""

import os
import re
from pathlib import Path

# 設定檔案路徑
SERVICES_DIR = Path(__file__).parent / "src" / "services"

# 定義檔案對應關係
FILE_MAPPINGS = [
    {
        "old_file": "userLogService.ts",
        "new_file": "userLogsService.ts",
        "replacements": [
            (r"'/api/userlogs'", "'/api/user_logs'"),
            (r'"user_detail_id"', '"user_id"'),
            (r'\buser_detail_id\b', 'user_id'),
            (r'\bsysfunction_id\b', 'system_function_id'),
            (r'UserLogService', 'UserLogsService'),
        ]
    },
    {
        "old_file": "userRoleService.ts",
        "new_file": "userRolesService.ts",
        "replacements": [
            (r"'/api/user_role'", "'/api/user_roles'"),
            (r'UserRoleService', 'UserRolesService'),
        ]
    },
    {
        "old_file": "roleRightService.ts",
        "new_file": "roleRightsService.ts",
        "replacements": [
            (r"'/api/role_right'", "'/api/role_rights'"),
            (r'\bsysfunction_id\b', 'system_function_id'),
            (r'RoleRightService', 'RoleRightsService'),
        ]
    }
]


def process_file(mapping: dict) -> bool:
    """處理單一檔案的替換"""
    old_path = SERVICES_DIR / mapping["old_file"]
    new_path = SERVICES_DIR / mapping["new_file"]

    if not old_path.exists():
        print(f"[SKIP] 來源檔案不存在: {old_path}")
        return False

    print(f"\n處理檔案: {mapping['old_file']} -> {mapping['new_file']}")

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
    print("建立新版前端服務檔案")
    print("=" * 80)

    success_count = 0
    fail_count = 0

    for mapping in FILE_MAPPINGS:
        if process_file(mapping):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 80)
    print(f"處理完成: 成功 {success_count} 個，失敗/跳過 {fail_count} 個")
    print("=" * 80)


if __name__ == "__main__":
    main()
