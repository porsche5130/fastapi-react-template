"""
PA6.4 Backend Main Application
FastAPI 主應用程式
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.routes import (
    auth, system, organization, sys_profile,
    users, permissions,
    systemcode, system_functions, system_notifications,
    user_roles, role_rights, user_logs, home
)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 建立 FastAPI 應用程式
app = FastAPI(
    title="PA6.4 Management System API",
    description="Paris Agreement Article 6.4 管理系統 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載靜態檔案
app.mount("/images", StaticFiles(directory=str(settings.images_path)), name="images")
app.mount("/uploads", StaticFiles(directory=str(settings.uploads_path)), name="uploads")
app.mount("/locales", StaticFiles(directory=str(settings.locales_path)), name="locales")

# 註冊路由
app.include_router(auth.router, prefix="/api/auth", tags=["認證"])
app.include_router(home.router, prefix="/api/home", tags=["系統首頁"])
app.include_router(system.router, prefix="/api/system", tags=["系統管理"])
app.include_router(organization.router, prefix="/api/organizations", tags=["組織管理"])
app.include_router(sys_profile.router, prefix="/api/sys_profiles", tags=["系統設定"])

# 使用者角色管理
app.include_router(user_roles.router, prefix="/api/user_roles", tags=["使用者角色管理"])

app.include_router(users.router, prefix="/api/users", tags=["使用者管理"])

# 系統功能管理
app.include_router(system_functions.router, prefix="/api/system_functions", tags=["系統功能管理"])

# 系統通知管理
app.include_router(system_notifications.router, prefix="/api/system_notifications", tags=["系統通知管理"])

# 角色權限管理
app.include_router(role_rights.router, prefix="/api/role_rights", tags=["角色權限管理"])

app.include_router(permissions.router, prefix="/api/permissions", tags=["權限查詢"])

# 使用者日誌
app.include_router(user_logs.router, prefix="/api/user_logs", tags=["使用者日誌"])

app.include_router(systemcode.router, prefix="/api/system_codes", tags=["系統代碼管理"])

@app.get("/", tags=["根路徑"])
async def root():
    """API 根路徑"""
    return {
        "message": "PA6.4 Management System API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }


@app.get("/api/health", tags=["健康檢查"])
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/debug/routes", tags=["調試"])
async def debug_routes():
    """列出所有路由（僅供調試）"""
    routes_info = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes_info.append({
                "path": route.path,
                "methods": list(route.methods) if hasattr(route, 'methods') else []
            })
    return {"total_routes": len(routes_info), "routes": routes_info}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
