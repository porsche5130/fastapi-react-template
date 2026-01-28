#!/usr/bin/env python3
"""
將 PA6.4 專案轉換為通用範本的腳本

使用方式:
1. 先複製整個專案到新目錄
2. 在新目錄中執行此腳本
3. 手動檢查替換結果
"""

import os
import sys
from pathlib import Path
from typing import Dict, Set

# 替換映射
REPLACEMENTS: Dict[str, str] = {
    'PA6.4': 'TEMPLATE',
    'pa64': 'template',
    'PA64': 'TEMPLATE',
    'Paris Agreement Article 6.4': 'FastAPI React Multi-Tenant Template',
    'Paris Agreement Article 6.4 管理系統': '多租戶管理系統',
    'PA6.4 減碳專案': '示範組織',
    'PA6.4 系統': '多租戶系統',
    'PA6.4 管理系統': '多租戶管理系統',
}

# 需要處理的檔案類型
FILE_EXTENSIONS = {
    '.py', '.md', '.json', '.ts', '.tsx', '.sql',
    '.yml', '.yaml', '.txt', '.env.example', '.sh', '.bat'
}

# 排除的目錄
EXCLUDE_DIRS = {
    'node_modules', '__pycache__', '.git', 'venv',
    'build', 'dist', 'env', 'ENV', '.venv',
    'sharedata/images', 'sharedata/uploads', 'sharedata/temp'
}

# 排除的檔案
EXCLUDE_FILES = {
    '.env',  # 不處理實際的環境變數檔案
    'package-lock.json',
    'yarn.lock',
}

def should_process_file(file_path: Path, root_dir: Path) -> bool:
    """判斷檔案是否需要處理"""
    # 檢查是否在排除的目錄中
    relative_path = file_path.relative_to(root_dir)
    for excluded in EXCLUDE_DIRS:
        if excluded in str(relative_path).split(os.sep):
            return False

    # 檢查是否在排除的檔案中
    if file_path.name in EXCLUDE_FILES:
        return False

    # 檢查副檔名
    return file_path.suffix in FILE_EXTENSIONS or file_path.name == '.env.example'

def replace_in_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    替換檔案內容

    Args:
        file_path: 檔案路徑
        dry_run: 是否為測試模式 (不實際寫入)

    Returns:
        是否有進行替換
    """
    try:
        # 讀取檔案
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # 執行替換
        for old, new in REPLACEMENTS.items():
            content = content.replace(old, new)

        # 檢查是否有變更
        if content != original_content:
            if not dry_run:
                file_path.write_text(content, encoding='utf-8')
            return True

        return False

    except UnicodeDecodeError:
        # 嘗試使用其他編碼
        try:
            content = file_path.read_text(encoding='utf-8-sig')
            original_content = content

            for old, new in REPLACEMENTS.items():
                content = content.replace(old, new)

            if content != original_content:
                if not dry_run:
                    file_path.write_text(content, encoding='utf-8')
                return True

            return False
        except Exception as e:
            print(f"⚠️  無法讀取: {file_path} - {e}")
            return False

    except Exception as e:
        print(f"✗ 錯誤: {file_path} - {e}")
        return False

def rename_file_if_needed(file_path: Path, dry_run: bool = False) -> Path:
    """
    如果檔案名稱包含需要替換的字串,進行重新命名

    Returns:
        新的檔案路徑 (如果有重新命名) 或原路徑
    """
    old_name = file_path.name
    new_name = old_name

    for old, new in REPLACEMENTS.items():
        new_name = new_name.replace(old, new)

    if new_name != old_name:
        new_path = file_path.parent / new_name
        if not dry_run:
            file_path.rename(new_path)
        print(f"  📝 重新命名: {old_name} → {new_name}")
        return new_path

    return file_path

def main():
    """主程式"""
    # 檢查參數
    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv

    if dry_run:
        print("🔍 測試模式 (不會實際修改檔案)")
        print()

    # 確定根目錄
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        root_dir = Path(sys.argv[1]).resolve()
    else:
        root_dir = Path.cwd()

    if not root_dir.exists():
        print(f"❌ 錯誤: 目錄不存在 - {root_dir}")
        sys.exit(1)

    print("=" * 70)
    print("🚀 PA6.4 → 通用範本轉換腳本")
    print("=" * 70)
    print()
    print(f"📁 根目錄: {root_dir}")
    print()
    print("🔄 替換規則:")
    for old, new in REPLACEMENTS.items():
        print(f"  • {old:40} → {new}")
    print()

    # 確認
    if not dry_run:
        response = input("⚠️  這將修改檔案內容,確定要繼續嗎? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("已取消")
            sys.exit(0)
        print()

    # 處理檔案
    print("📝 處理檔案...")
    print()

    updated_count = 0
    renamed_count = 0

    # 收集所有需要處理的檔案
    files_to_process = []
    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and should_process_file(file_path, root_dir):
            files_to_process.append(file_path)

    print(f"找到 {len(files_to_process)} 個檔案需要檢查")
    print()

    for file_path in files_to_process:
        relative_path = file_path.relative_to(root_dir)

        # 替換檔案內容
        if replace_in_file(file_path, dry_run):
            print(f"✓ 已更新: {relative_path}")
            updated_count += 1

        # 檢查檔案名稱
        new_path = rename_file_if_needed(file_path, dry_run)
        if new_path != file_path:
            renamed_count += 1

    print()
    print("=" * 70)
    print("✅ 轉換完成!")
    print("=" * 70)
    print()
    print(f"📊 統計:")
    print(f"  • 檢查檔案: {len(files_to_process)}")
    print(f"  • 更新檔案: {updated_count}")
    print(f"  • 重新命名: {renamed_count}")
    print()

    if not dry_run:
        print("⚠️  請手動檢查以下項目:")
        print()
        print("  1. README.md")
        print("     - 更新專案描述")
        print("     - 更新功能說明")
        print()
        print("  2. CHANGELOG.md")
        print("     - 重置版本歷史")
        print("     - 記錄為範本初始版本")
        print()
        print("  3. Develop/backend/app/core/init_data.py")
        print("     - 檢查初始組織資料")
        print("     - 更新示範資料")
        print()
        print("  4. Develop/frontend/src/locales/")
        print("     - 更新應用名稱翻譯")
        print("     - 移除業務特定文字")
        print()
        print("  5. Develop/backend/.env.example")
        print("     - 確認資料庫名稱")
        print("     - 確認範例值")
        print()
        print("  6. PACKAGE_COMPLETE.md")
        print("     - 更新為範本說明")
        print("     - 或考慮刪除 (這是 PA6.4 特定文件)")
        print()
        print("📦 下一步:")
        print()
        print("  # 初始化 Git")
        print("  git init")
        print("  git add .")
        print("  git commit -m \"Initial commit: Multi-tenant template\"")
        print()
        print("  # 推送到 GitHub")
        print("  git remote add origin https://github.com/你的帳號/倉庫名稱.git")
        print("  git push -u origin main")
        print()
    else:
        print("ℹ️  這是測試模式,沒有實際修改檔案")
        print("   移除 --dry-run 參數以實際執行")
        print()

if __name__ == '__main__':
    main()
