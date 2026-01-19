"""
Database Connection and Session Management
資料庫連線與 Session 管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# 建立資料庫引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 檢查連線是否有效
    pool_recycle=3600,   # 每小時回收連線
    echo=settings.DEBUG  # 開發環境顯示 SQL
)

# 建立 SessionLocal 類別
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 建立 Base 類別
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    取得資料庫 Session 的依賴注入函數

    使用範例:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
