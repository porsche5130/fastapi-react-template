"""
Sequence Rules Model
編號規則設定模型
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SequenceRule(Base):
    """編號規則設定表"""

    __tablename__ = "sequence_rules"

    # 主鍵
    id = Column(Integer, primary_key=True, index=True)

    # 規則識別
    rule_code = Column(String(50), nullable=False, unique=True, index=True, comment="規則代碼")
    rule_name = Column(String(200), nullable=False, comment="規則名稱")
    description = Column(Text, comment="規則說明")

    # 格式設定
    prefix = Column(String(20), comment="前置字串")
    date_format = Column(String(20), comment="日期格式 (YYYY, YYYYMM, YYYYMMDD)")
    sequence_length = Column(Integer, nullable=False, default=6, comment="流水號長度")
    suffix = Column(String(20), comment="後置字串")
    separator = Column(String(5), default="-", comment="分隔符號")

    # 重置機制
    reset_mode = Column(
        String(20),
        nullable=False,
        default="never",
        comment="重置模式"
    )

    # 範例與狀態
    example = Column(String(200), comment="格式範例")
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否啟用")

    # 組織與權限
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, default=1, comment="組織ID")

    # 系統欄位
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="建立者ID")
    updated_by = Column(Integer, ForeignKey("users.id"), comment="更新者ID")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), comment="建立時間")
    updated_at = Column(TIMESTAMP, comment="更新時間")

    # 約束
    __table_args__ = (
        CheckConstraint(
            "reset_mode IN ('never', 'yearly', 'monthly', 'daily')",
            name="chk_sequence_rules_reset_mode"
        ),
        Index("idx_sequence_rules_code", "rule_code"),
        Index("idx_sequence_rules_active", "is_active"),
        Index("idx_sequence_rules_org", "org_id"),
    )

    # 關聯
    organization = relationship("Organization", foreign_keys=[org_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    values = relationship("SequenceValue", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SequenceRule(id={self.id}, rule_code='{self.rule_code}', example='{self.example}')>"


class SequenceValue(Base):
    """編號規則當前值表"""

    __tablename__ = "sequence_values"

    # 主鍵
    id = Column(Integer, primary_key=True, index=True)

    # 關聯規則
    rule_id = Column(Integer, ForeignKey("sequence_rules.id", ondelete="CASCADE"), nullable=False, comment="規則ID")

    # 期間識別
    period = Column(String(20), nullable=False, comment="期間識別")

    # 當前值
    current_value = Column(Integer, nullable=False, default=0, comment="當前流水號")
    last_generated_at = Column(TIMESTAMP, comment="最後產生時間")

    # 組織
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, default=1, comment="組織ID")

    # 系統欄位
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), comment="建立時間")
    updated_at = Column(TIMESTAMP, comment="更新時間")

    # 約束
    __table_args__ = (
        Index("uk_sequence_values", "rule_id", "period", "org_id", unique=True),
        Index("idx_sequence_values_rule", "rule_id"),
        Index("idx_sequence_values_period", "period"),
        Index("idx_sequence_values_org", "org_id"),
    )

    # 關聯
    rule = relationship("SequenceRule", back_populates="values")
    organization = relationship("Organization", foreign_keys=[org_id])

    def __repr__(self):
        return f"<SequenceValue(id={self.id}, rule_id={self.rule_id}, period='{self.period}', current_value={self.current_value})>"
