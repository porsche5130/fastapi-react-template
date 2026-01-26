"""
Sequence Service
編號產生服務
"""

import logging
from datetime import datetime, date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import HTTPException, status

from app.models.sequence_rules import SequenceRule, SequenceValue

logger = logging.getLogger(__name__)


class SequenceService:
    """編號產生服務類別"""

    @staticmethod
    def generate_number(
        db: Session,
        rule_code: str,
        org_id: int,
        custom_date: Optional[date] = None
    ) -> dict:
        """
        產生編號

        Args:
            db: 資料庫 Session
            rule_code: 規則代碼
            org_id: 組織 ID
            custom_date: 自訂日期 (預設為今天)

        Returns:
            dict: {
                "number": "ORD-20260124-000001",
                "rule_code": "ORDER_NO",
                "sequence_value": 1,
                "period": "20260124",
                "generated_at": datetime
            }

        Raises:
            HTTPException: 規則不存在、未啟用等錯誤
        """
        # 1. 取得規則
        rule = db.query(SequenceRule).filter(
            and_(
                SequenceRule.rule_code == rule_code,
                SequenceRule.org_id == org_id,
                SequenceRule.is_active == True
            )
        ).first()

        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"編號規則不存在或未啟用: {rule_code}"
            )

        # 2. 計算期間識別
        target_date = custom_date if custom_date else date.today()
        period = SequenceService._calculate_period(rule.reset_mode, rule.date_format, target_date)

        # 3. 取得或建立當前值記錄 (使用資料庫鎖定防止併發問題)
        seq_value = db.query(SequenceValue).filter(
            and_(
                SequenceValue.rule_id == rule.id,
                SequenceValue.period == period,
                SequenceValue.org_id == org_id
            )
        ).with_for_update().first()

        if not seq_value:
            # 建立新的期間記錄
            seq_value = SequenceValue(
                rule_id=rule.id,
                period=period,
                current_value=0,
                org_id=org_id
            )
            db.add(seq_value)
            db.flush()

        # 4. 遞增流水號
        seq_value.current_value += 1
        seq_value.last_generated_at = datetime.now()
        seq_value.updated_at = datetime.now()

        # 5. 組合完整編號
        full_number = SequenceService._build_number(
            rule=rule,
            sequence_value=seq_value.current_value,
            period=period
        )

        # 6. 提交變更
        db.commit()

        logger.info(
            f"[Sequence] 產生編號: {full_number} "
            f"(rule={rule_code}, period={period}, seq={seq_value.current_value})"
        )

        return {
            "number": full_number,
            "rule_code": rule_code,
            "sequence_value": seq_value.current_value,
            "period": period,
            "generated_at": datetime.now()
        }

    @staticmethod
    def _calculate_period(reset_mode: str, date_format: Optional[str], target_date: date) -> str:
        """
        計算期間識別

        Args:
            reset_mode: 重置模式 (never, yearly, monthly, daily)
            date_format: 日期格式 (YYYY, YYYYMM, YYYYMMDD)
            target_date: 目標日期

        Returns:
            str: 期間識別字串
        """
        if reset_mode == "never":
            return "PERMANENT"
        elif reset_mode == "yearly":
            return target_date.strftime("%Y")
        elif reset_mode == "monthly":
            return target_date.strftime("%Y%m")
        elif reset_mode == "daily":
            return target_date.strftime("%Y%m%d")
        else:
            return "PERMANENT"

    @staticmethod
    def _build_number(rule: SequenceRule, sequence_value: int, period: str) -> str:
        """
        組合完整編號

        Args:
            rule: 編號規則
            sequence_value: 流水號
            period: 期間識別

        Returns:
            str: 完整編號
        """
        parts = []

        # 1. 前置字串
        if rule.prefix:
            parts.append(rule.prefix)

        # 2. 日期部分 (如果有 date_format)
        if rule.date_format:
            # period 已經是正確的格式 (YYYY, YYYYMM, YYYYMMDD)
            parts.append(period)

        # 3. 流水號 (自動補0)
        sequence_str = str(sequence_value).zfill(rule.sequence_length)
        parts.append(sequence_str)

        # 4. 後置字串
        if rule.suffix:
            parts.append(rule.suffix)

        # 5. 組合 (使用分隔符號)
        separator = rule.separator if rule.separator else ""
        return separator.join(parts)

    @staticmethod
    def preview_number(rule_code: str, db: Session, org_id: int) -> dict:
        """
        預覽下一個編號 (不實際產生)

        Args:
            rule_code: 規則代碼
            db: 資料庫 Session
            org_id: 組織 ID

        Returns:
            dict: 預覽資訊
        """
        rule = db.query(SequenceRule).filter(
            and_(
                SequenceRule.rule_code == rule_code,
                SequenceRule.org_id == org_id
            )
        ).first()

        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"編號規則不存在: {rule_code}"
            )

        # 計算期間
        period = SequenceService._calculate_period(
            rule.reset_mode,
            rule.date_format,
            date.today()
        )

        # 取得當前值
        seq_value = db.query(SequenceValue).filter(
            and_(
                SequenceValue.rule_id == rule.id,
                SequenceValue.period == period,
                SequenceValue.org_id == org_id
            )
        ).first()

        next_value = (seq_value.current_value + 1) if seq_value else 1

        # 組合預覽編號
        preview_number = SequenceService._build_number(
            rule=rule,
            sequence_value=next_value,
            period=period
        )

        return {
            "preview_number": preview_number,
            "rule_code": rule_code,
            "next_sequence_value": next_value,
            "period": period,
            "current_value": seq_value.current_value if seq_value else 0
        }

    @staticmethod
    def reset_sequence(rule_code: str, db: Session, org_id: int, period: Optional[str] = None) -> dict:
        """
        重置流水號

        Args:
            rule_code: 規則代碼
            db: 資料庫 Session
            org_id: 組織 ID
            period: 要重置的期間 (預設為當前期間)

        Returns:
            dict: 重置結果
        """
        rule = db.query(SequenceRule).filter(
            and_(
                SequenceRule.rule_code == rule_code,
                SequenceRule.org_id == org_id
            )
        ).first()

        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"編號規則不存在: {rule_code}"
            )

        # 計算期間
        if not period:
            period = SequenceService._calculate_period(
                rule.reset_mode,
                rule.date_format,
                date.today()
            )

        # 重置流水號
        seq_value = db.query(SequenceValue).filter(
            and_(
                SequenceValue.rule_id == rule.id,
                SequenceValue.period == period,
                SequenceValue.org_id == org_id
            )
        ).first()

        if seq_value:
            old_value = seq_value.current_value
            seq_value.current_value = 0
            seq_value.updated_at = datetime.now()
            db.commit()

            logger.warning(
                f"[Sequence] 重置流水號: rule={rule_code}, period={period}, "
                f"old_value={old_value}, new_value=0"
            )

            return {
                "message": "流水號已重置",
                "rule_code": rule_code,
                "period": period,
                "old_value": old_value,
                "new_value": 0
            }
        else:
            return {
                "message": "該期間尚未產生任何編號",
                "rule_code": rule_code,
                "period": period
            }
