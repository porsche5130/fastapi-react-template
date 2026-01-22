"""
批次替換 user_detail 為 users 的腳本
"""
import os
import re
from pathlib import Path

def replace_in_file(file_path):
    """替換單個檔案中的內容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 替換規則
        replacements = [
            # Import statements
            (r'from app\.models\.user_detail import UserDetail', 'from app.models.user import User'),
            # Class references
            (r'\bUserDetail\b', 'User'),
            # ForeignKey table references
            (r'ForeignKey\("user_detail\.', 'ForeignKey("users.'),
            # Index names
            (r'idx_user_detail_', 'idx_users_'),
            # relationship back_populates (需要檢查context)
            # 這個不能全局替換,需要手動處理
        ]

        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)

        # 只有內容有變化才寫入
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, file_path
        return False, file_path
    except Exception as e:
        return None, f"Error processing {file_path}: {str(e)}"

def main():
    """主函數"""
    # 需要處理的目錄
    directories = [
        Path("app/models"),
        Path("app/routes"),
        Path("app/core"),
        Path("app/schemas"),
        Path("app/services"),
    ]

    modified_files = []
    error_files = []
    skipped_files = []

    for directory in directories:
        if not directory.exists():
            print(f"Directory not found: {directory}")
            continue

        for file_path in directory.rglob("*.py"):
            # 跳過 __pycache__ 和已重命名的 user.py
            if "__pycache__" in str(file_path) or file_path.name == "user.py":
                continue

            result, info = replace_in_file(file_path)

            if result is True:
                modified_files.append(info)
                print(f"Modified: {file_path}")
            elif result is False:
                skipped_files.append(info)
            else:
                error_files.append(info)
                print(f"Error: {info}")

    # 輸出總結
    print("\n" + "="*80)
    print("Summary:")
    print(f"Modified: {len(modified_files)} files")
    print(f"Skipped: {len(skipped_files)} files (no changes needed)")
    print(f"Errors: {len(error_files)} files")

    if modified_files:
        print("\nModified files:")
        for f in modified_files:
            print(f"  - {f}")

    if error_files:
        print("\nErrors:")
        for e in error_files:
            print(f"  - {e}")

if __name__ == "__main__":
    main()
