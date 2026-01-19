"""
直接運行服務器並檢查路由
"""
import uvicorn
from app.main import app

# 列出所有路由
print("\n=== 註冊的路由 ===")
for route in app.routes:
    if hasattr(route, 'path'):
        methods = list(route.methods) if hasattr(route, 'methods') else []
        print(f"{route.path} - {methods}")

print("\n=== 啟動服務器 ===")
uvicorn.run(app, host="0.0.0.0", port=10181, reload=False)
