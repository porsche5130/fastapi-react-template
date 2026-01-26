"""
PA6.4 Backend Main Application
FastAPI 主應用程式
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.core.config import settings
from app.core.redis_client import init_redis, close_redis, redis_health_check
from app.routes import (
    auth, system, organization, sys_profile,
    users, permissions,
    systemcode, system_functions, system_notifications,
    user_roles, role_rights, user_logs, home, transaction,
    numbering_rules, file_attachments
)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# 生命週期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時執行
    logger.info("🚀 應用程式啟動中...")

    # 初始化 Redis
    try:
        init_redis(
            host=getattr(settings, 'REDIS_HOST', 'localhost'),
            port=getattr(settings, 'REDIS_PORT', 6379),
            db=getattr(settings, 'REDIS_DB', 0),
            password=getattr(settings, 'REDIS_PASSWORD', None)
        )
    except Exception as e:
        logger.warning(f"⚠️  Redis 初始化失敗,使用記憶體儲存: {e}")

    logger.info("✅ 應用程式啟動完成")

    yield  # 應用程式運行期間

    # 關閉時執行
    logger.info("🛑 應用程式關閉中...")
    close_redis()
    logger.info("✅ 應用程式已關閉")


# 建立 FastAPI 應用程式
app = FastAPI(
    title="PA6.4 Management System API",
    description="Paris Agreement Article 6.4 管理系統 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Exception handlers for better debugging
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """處理請求驗證錯誤，記錄詳細資訊"""
    logger.error(f"❌ Request Validation Error at {request.url}")
    logger.error(f"   Errors: {exc.errors()}")
    logger.error(f"   Body: {exc.body}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """處理 Pydantic 驗證錯誤（response model）"""
    logger.error(f"❌ Pydantic Validation Error at {request.url}")
    logger.error(f"   Errors: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
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
app.include_router(transaction.router, prefix="/api/transaction", tags=["交易令牌"])
app.include_router(home.router, prefix="/api/home", tags=["系統首頁"])
app.include_router(system.router, prefix="/api/system", tags=["系統管理"])
app.include_router(organization.router, prefix="/api/organizations", tags=["組織管理"])
app.include_router(sysprofile.router, prefix="/api/sys_profiles", tags=["系統設定"])

# 使用者角色管理
app.include_router(userrole.router, prefix="/api/user_roles", tags=["使用者角色管理"])

app.include_router(user.router, prefix="/api/users", tags=["使用者管理"])

# 系統功能管理
app.include_router(systemfunction.router, prefix="/api/system_functions", tags=["系統功能管理"])

# 系統通知管理
app.include_router(systemnotification.router, prefix="/api/system_notifications", tags=["系統通知管理"])

# 角色權限管理
app.include_router(roleright.router, prefix="/api/role_rights", tags=["角色權限管理"])

app.include_router(permissions.router, prefix="/api/permissions", tags=["權限查詢"])

# 使用者日誌
app.include_router(userlog.router, prefix="/api/user_logs", tags=["使用者日誌"])

app.include_router(systemcode.router, prefix="/api/system_codes", tags=["系統代碼管理"])

# 編號規則管理
app.include_router(numberingrule.router, prefix="/api/numbering-rules", tags=["編號規則設定"])

# 檔案附件管理
app.include_router(fileattachment.router, prefix="/api/file-attachments", tags=["檔案附件管理"])

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
    redis_status = "healthy" if redis_health_check() else "unavailable (using memory storage)"

    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "redis": redis_status
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
