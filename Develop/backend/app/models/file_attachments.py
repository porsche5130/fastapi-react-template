"""
File Attachments Model
檔案附件管理模型
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, BigInteger, ForeignKey, CheckConstraint, Index, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class FileAttachment(Base):
    """檔案附件管理表"""

    __tablename__ = "file_attachments"

    # 主鍵
    id = Column(Integer, primary_key=True, index=True)

    # 檔案基本資訊
    original_name = Column(String(500), nullable=False, comment="原始檔案名稱")
    storage_path = Column(String(1000), nullable=False, comment="儲存路徑")
    file_size = Column(BigInteger, nullable=False, comment="檔案大小 (bytes)")
    mime_type = Column(String(200), nullable=False, comment="MIME 類型")
    file_hash = Column(String(64), nullable=False, index=True, comment="SHA-256 雜湊")

    # 分類與業務關聯
    category = Column(
        String(50),
        nullable=False,
        comment="檔案分類"
    )
    business_type = Column(String(50), comment="業務類型")
    related_table = Column(String(100), comment="關聯的資料表名稱")
    related_id = Column(Integer, comment="關聯的記錄 ID")

    # 存取控制
    access_level = Column(
        String(20),
        nullable=False,
        default="private",
        comment="存取等級"
    )
    is_public = Column(Boolean, nullable=False, default=False, comment="是否公開")
    allowed_roles = Column(ARRAY(Text), comment="允許存取的角色列表")
    allowed_users = Column(ARRAY(Integer), comment="允許存取的使用者 ID 列表")

    # 檔案狀態
    is_temp = Column(Boolean, nullable=False, default=True, index=True, comment="是否為臨時檔案")
    confirmed_at = Column(TIMESTAMP, comment="確認時間")
    download_count = Column(Integer, nullable=False, default=0, comment="下載次數")
    last_downloaded_at = Column(TIMESTAMP, comment="最後下載時間")

    # 版本控制
    version = Column(Integer, nullable=False, default=1, comment="檔案版本號")
    previous_version_id = Column(
        Integer,
        ForeignKey("file_attachments.id", ondelete="SET NULL"),
        comment="前一版本的檔案 ID"
    )

    # 附加資訊
    thumbnail_path = Column(String(1000), comment="縮圖路徑")
    file_metadata = Column(JSONB, comment="其他中繼資料")
    description = Column(Text, comment="檔案說明")
    tags = Column(ARRAY(Text), comment="標籤")

    # 有效期限
    expires_at = Column(TIMESTAMP, comment="過期時間")

    # 組織與使用者
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, default=1, comment="組織ID")
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="上傳者ID")

    # 系統欄位
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), comment="建立時間")
    updated_at = Column(TIMESTAMP, comment="更新時間")

    # 約束
    __table_args__ = (
        CheckConstraint(
            "category IN ('image', 'document', 'archive', 'video', 'audio', 'other')",
            name="chk_file_attachments_category"
        ),
        CheckConstraint(
            "access_level IN ('public', 'private', 'restricted')",
            name="chk_file_attachments_access_level"
        ),
        Index("idx_file_attachments_hash", "file_hash"),
        Index("idx_file_attachments_category", "category"),
        Index("idx_file_attachments_business", "business_type", "related_id"),
        Index("idx_file_attachments_uploader", "uploaded_by"),
        Index("idx_file_attachments_org", "org_id"),
        Index("idx_file_attachments_temp", "is_temp", "created_at"),
        Index("idx_file_attachments_access", "access_level"),
    )

    # 關聯
    organization = relationship("Organization", foreign_keys=[org_id])
    uploader = relationship("User", foreign_keys=[uploaded_by])
    previous_version = relationship("FileAttachment", remote_side=[id], foreign_keys=[previous_version_id])

    def __repr__(self):
        return f"<FileAttachment(id={self.id}, original_name='{self.original_name}', size={self.file_size})>"
