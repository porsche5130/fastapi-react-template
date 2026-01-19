"""
User Log Model
作業紀錄表
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserLog(Base):
    """作業紀錄表"""

    __tablename__ = "userlogs"

    # 主鍵
    id = Column(Integer, primary_key=True, index=True)

    # 作業資訊
    user_detail_id = Column(Integer, ForeignKey("user_detail.id"), nullable=False, index=True)
    sysfuction_id = Column(Integer, ForeignKey("sysfuction.id"), nullable=False, index=True)
    module_item = Column(String(50), nullable=False, index=True)  # Create/Read/Update/Delete/Print/File

    # 資料記錄
    look_data = Column(JSONB, nullable=False, default=dict)
    change_data = Column(JSONB, nullable=False, default=dict)

    # 時間與錯誤
    action_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), index=True)
    err_detail = Column(String(2000))

    # 約束
    __table_args__ = (
        CheckConstraint(
            "module_item IN ('Create', 'Read', 'Update', 'Delete', 'Print', 'File')",
            name="chk_module_item"
        ),
        Index("idx_userlogs_user", "user_detail_id"),
        Index("idx_userlogs_function", "sysfuction_id"),
        Index("idx_userlogs_action_at", "action_at"),
        Index("idx_userlogs_module", "module_item"),
    )

    # 關聯
    user = relationship("UserDetail", back_populates="logs")
    function = relationship("SysFunction", back_populates="logs")
