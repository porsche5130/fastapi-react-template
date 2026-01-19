"""
Application Configuration
使用 Pydantic Settings 管理環境變數
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from pathlib import Path


class Settings(BaseSettings):
    """應用程式設定"""

    # Application
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="DEBUG")
    PORT: int = Field(default=10181)

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://dev:dev123@localhost:5432/pa64_dev"
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://:!DC1qaz2wsx@localhost:6379/0"
    )

    # Security
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production"
    )
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:10180"]
    )

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = Field(default=50)
    ALLOWED_IMAGE_TYPES: List[str] = Field(
        default=[
            "image/png",
            "image/jpeg",
            "image/jpg",
            "image/gif",
            "image/svg+xml"
        ]
    )
    ALLOWED_DOCUMENT_TYPES: List[str] = Field(
        default=[
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ]
    )

    # Shared Data Directory
    SHAREDATA_DIR: str = Field(default="sharedata")

    @property
    def sharedata_path(self) -> Path:
        """共用資料目錄的絕對路徑"""
        base_dir = Path(__file__).parent.parent.parent
        return base_dir / self.SHAREDATA_DIR

    @property
    def images_path(self) -> Path:
        """圖片目錄"""
        return self.sharedata_path / "images"

    @property
    def uploads_path(self) -> Path:
        """上傳檔案目錄"""
        return self.sharedata_path / "uploads"

    @property
    def locales_path(self) -> Path:
        """語系檔案目錄"""
        return self.sharedata_path / "locales"

    class Config:
        env_file = ".env"
        case_sensitive = True


# 建立全域設定實例
settings = Settings()

# 確保目錄存在
settings.images_path.mkdir(parents=True, exist_ok=True)
settings.uploads_path.mkdir(parents=True, exist_ok=True)
settings.locales_path.mkdir(parents=True, exist_ok=True)
