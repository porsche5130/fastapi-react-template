"""
PA6.4 Backend Main Application
FastAPI 主應用程式
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.routes import auth, system, organization, sys_profile, user_role, user_detail, sysfunction, role_right, permissions, userlog

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
app.include_router(system.router, prefix="/api/system", tags=["系統管理"])
app.include_router(organization.router, prefix="/api/organizations", tags=["組織管理"])
app.include_router(sys_profile.router, prefix="/api/sys_profile", tags=["系統設定"])
app.include_router(user_role.router, prefix="/api/user_role", tags=["使用者角色管理"])
app.include_router(user_detail.router, prefix="/api/user_detail", tags=["使用者管理"])
app.include_router(sysfunction.router, prefix="/api/sysfunction", tags=["系統功能管理"])
app.include_router(role_right.router, prefix="/api/role_right", tags=["角色權限管理"])
app.include_router(permissions.router, prefix="/api/permissions", tags=["權限查詢"])
app.include_router(userlog.router, prefix="/api/userlogs", tags=["使用者日誌"])

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
