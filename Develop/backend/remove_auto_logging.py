"""
移除後端所有 route 中的自動日誌記錄程式碼
"""
import re
from pathlib import Path

# 要處理的檔案列表
files_to_process = [
    "app/routes/organization.py",
    "app/routes/user_role.py",
    "app/routes/user_detail.py",
    "app/routes/sysfunction.py",
    "app/routes/sys_profile.py",
    "app/routes/role_right.py",
    "app/routes/userlog.py"
]

def remove_logging_blocks(content: str) -> str:
    """移除所有 UserLogService 的程式碼區塊（log_view, log_read, log_create, log_update, log_delete）"""

    # Pattern 1: 移除帶註解的日誌區塊
    pattern1 = r'\n\s*#\s*記錄.*?日誌.*?\n\s*try:.*?UserLogService\.log_\w+\(.*?\).*?except Exception as e:.*?logger\.error\(.*?\)\n'
    content = re.sub(pattern1, '\n', content, flags=re.DOTALL)

    # Pattern 2: 移除不帶註解的日誌區塊（包括操作日誌、功能瀏覽等）
    pattern2 = r'\n\s*try:.*?UserLogService\.log_\w+\(.*?\).*?except Exception as e:.*?logger\.error\(.*?\)\n'
    content = re.sub(pattern2, '\n', content, flags=re.DOTALL)

    # Pattern 3: 移除單行註解（# 記錄操作日誌）
    pattern3 = r'\n\s*#\s*記錄操作日誌\s*\n'
    content = re.sub(pattern3, '\n', content, flags=re.DOTALL)

    return content

# 處理每個檔案
for file_path in files_to_process:
    full_path = Path(file_path)
    if not full_path.exists():
        print(f"File not found: {file_path}")
        continue

    print(f"Processing: {file_path}")

    # 讀取檔案
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 移除日誌記錄區塊
    new_content = remove_logging_blocks(content)

    # 寫回檔案
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Completed: {file_path}")

print("\nAll files processed!")
