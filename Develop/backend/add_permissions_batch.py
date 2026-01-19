"""
批量添加權限檢查腳本
為 user_role, user_detail, sysfunction 路由添加權限檢查
"""

import re

routes_config = [
    {
        "file": "app/routes/user_role.py",
        "func_code": "user_role",
        "import_line": "from app.core.deps import get_current_user",
        "new_import": "from app.core.deps import get_current_user\nfrom app.core.permissions import check_permission"
    },
    {
        "file": "app/routes/user_detail.py",
        "func_code": "user_detail",
        "import_line": "from app.core.deps import get_current_user",
        "new_import": "from app.core.deps import get_current_user\nfrom app.core.permissions import check_permission"
    },
    {
        "file": "app/routes/sysfunction.py",
        "func_code": "sysfunction",
        "import_line": "from app.core.deps import get_current_user",
        "new_import": "from app.core.deps import get_current_user\nfrom app.core.permissions import check_permission"
    }
]

# 權限檢查代碼模板
permission_checks = {
    "read": '''
    # 檢查權限
    if not check_permission(db, current_user, "{func_code}", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限讀取{resource}"
        )
''',
    "create": '''
    # 檢查權限
    if not check_permission(db, current_user, "{func_code}", "create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限新增{resource}"
        )
''',
    "update": '''
    # 檢查權限
    if not check_permission(db, current_user, "{func_code}", "update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限修改{resource}"
        )
''',
    "delete": '''
    # 檢查權限
    if not check_permission(db, current_user, "{func_code}", "delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限刪除{resource}"
        )
'''
}

resource_names = {
    "user_role": "使用者角色",
    "user_detail": "使用者",
    "sysfunction": "系統功能"
}

def add_permission_check(content: str, func_code: str, route_type: str, resource: str) -> str:
    """在路由函數中添加權限檢查"""
    # 根據路由類型確定要插入權限檢查的位置
    if route_type == "get":
        permission_type = "read"
    elif route_type == "post":
        permission_type = "create"
    elif route_type == "put":
        permission_type = "update"
    elif route_type == "delete":
        permission_type = "delete"
    else:
        return content

    # 獲取權限檢查代碼
    check_code = permission_checks[permission_type].format(
        func_code=func_code,
        resource=resource
    )

    # 找到函數開始位置並插入權限檢查
    # 匹配模式: async def function_name(...): """docstring"""
    pattern = rf'(@router\.{route_type}\([^)]+\)[^\n]+\nasync def [^:]+:\s+"""[^"]+""")'

    def replacer(match):
        return match.group(1) + check_code

    new_content = re.sub(pattern, replacer, content, count=1)
    return new_content

# 注意:此腳本只是示例,實際執行需要手動修改
print("此腳本為輔助設計,實際需要手動使用 Edit 工具逐個修改")
