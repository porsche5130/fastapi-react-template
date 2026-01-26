"""
Dynamic Router
動態路由器 - 根據 system_functions 表自動產生路由映射
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.systemfunction import SystemFunction


class DynamicRouter:
    """動態路由器 - 管理功能與模組的對應關係"""

    def __init__(self):
        self._route_map: Dict[str, str] = {}
        self._function_map: Dict[int, dict] = {}

    def load_routes(self, db: Session) -> None:
        """
        從 system_functions 表載入所有路由映射

        Args:
            db: 資料庫 session
        """
        functions = db.query(SystemFunction).filter(
            SystemFunction.is_active == True,
            SystemFunction.func_type == 2  # 只載入功能（非節點）
        ).all()

        self._route_map.clear()
        self._function_map.clear()

        for func in functions:
            # 建立 func_code 到 module_code 的映射
            self._route_map[func.func_code] = func.module_code

            # 建立完整的功能資訊映射
            self._function_map[func.id] = {
                'id': func.id,
                'func_code': func.func_code,
                'module_code': func.module_code,
                'func_cname': func.func_cname,
                'func_ename': func.func_ename,
                'func_order': func.func_order,
                'upper_func_id': func.upper_func_id,
                'is_mana': func.is_mana,
                'module_item': func.module_item,
                'description': func.description
            }

    def get_module_by_func_code(self, func_code: str) -> Optional[str]:
        """
        根據 func_code 取得對應的 module_code

        Args:
            func_code: 功能代碼

        Returns:
            module_code 或 None
        """
        return self._route_map.get(func_code)

    def get_api_route(self, func_code: str) -> Optional[str]:
        """
        根據 func_code 取得對應的 API 路由

        Args:
            func_code: 功能代碼

        Returns:
            API 路由路徑或 None
        """
        module_code = self.get_module_by_func_code(func_code)
        if not module_code:
            return None

        # 特殊處理認證相關路由
        if module_code in ['login', 'logout', 'change_password']:
            return f'/api/auth/{module_code}'

        # 一般路由格式
        return f'/api/{module_code}'

    def get_function_info(self, func_code: str) -> Optional[dict]:
        """
        根據 func_code 取得完整功能資訊

        Args:
            func_code: 功能代碼

        Returns:
            功能資訊字典或 None
        """
        for func_info in self._function_map.values():
            if func_info['func_code'] == func_code:
                return func_info
        return None

    def get_functions_by_module(self, module_code: str) -> List[dict]:
        """
        根據 module_code 取得所有使用該模組的功能

        Args:
            module_code: 模組代碼

        Returns:
            功能資訊列表
        """
        return [
            func_info for func_info in self._function_map.values()
            if func_info['module_code'] == module_code
        ]

    def get_all_routes(self) -> Dict[str, str]:
        """
        取得所有路由映射

        Returns:
            func_code 到 module_code 的映射字典
        """
        return self._route_map.copy()

    def get_menu_structure(self) -> List[dict]:
        """
        取得功能選單結構（樹狀）

        Returns:
            樹狀選單結構
        """
        # 取得所有父節點（upper_func_id = 0）
        root_functions = [
            func for func in self._function_map.values()
            if func['upper_func_id'] == 0
        ]

        # 遞迴建立樹狀結構
        def build_tree(parent_id: int) -> List[dict]:
            children = [
                func for func in self._function_map.values()
                if func['upper_func_id'] == parent_id
            ]

            result = []
            for child in sorted(children, key=lambda x: x['func_order']):
                node = child.copy()
                node['children'] = build_tree(child['id'])
                result.append(node)

            return result

        # 建立完整樹狀結構
        menu = []
        for root in sorted(root_functions, key=lambda x: x['func_order']):
            node = root.copy()
            node['children'] = build_tree(root['id'])
            menu.append(node)

        return menu

    def print_route_summary(self) -> None:
        """列印路由摘要資訊"""
        print("\n" + "="*80)
        print("動態路由器 - 路由映射摘要")
        print("="*80)

        # 按 func_order 排序
        sorted_functions = sorted(
            self._function_map.values(),
            key=lambda x: x['func_order']
        )

        print(f"\n{'func_code':<25} {'module_code':<25} {'API Route':<40}")
        print("-"*80)

        for func in sorted_functions:
            func_code = func['func_code']
            module_code = func['module_code']
            api_route = self.get_api_route(func_code)
            print(f"{func_code:<25} {module_code:<25} {api_route or 'N/A':<40}")

        print("-"*80)
        print(f"總計: {len(self._route_map)} 個功能路由")
        print("="*80 + "\n")


# 建立全域路由器實例
router = DynamicRouter()


def get_router() -> DynamicRouter:
    """取得全域路由器實例"""
    return router


def init_router(db: Session) -> None:
    """
    初始化路由器（應在應用啟動時呼叫）

    Args:
        db: 資料庫 session
    """
    router.load_routes(db)
    router.print_route_summary()
