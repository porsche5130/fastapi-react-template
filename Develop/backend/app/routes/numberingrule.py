"""
Numbering Rules Routes
編號規則設定 API
"""

import logging
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.routes.transaction import require_txn_token
from app.models.user import User
from app.models.sequence_rules import SequenceRule, SequenceValue
from app.schemas.sequence_rules import (
    SequenceRuleCreate,
    SequenceRuleUpdate,
    SequenceRuleResponse,
    SequenceRuleListResponse,
    GenerateNumberRequest,
    GenerateNumberResponse,
    SequenceValueResponse
)
from app.services.sequence_service import SequenceService

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ 編號規則 CRUD ============

@router.get("", response_model=SequenceRuleListResponse, summary="取得編號規則列表")
async def get_sequence_rules(
    skip: int = Query(0, ge=0, description="跳過筆數"),
    limit: int = Query(20, ge=1, le=100, description="每頁筆數"),
    is_active: Optional[bool] = Query(None, description="是否啟用"),
    search: Optional[str] = Query(None, description="搜尋關鍵字 (規則代碼或名稱)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("numbering_rules", "read"))
):
    """
    取得編號規則列表

    需要權限: numbering_rules.read
    """
    query = db.query(SequenceRule).filter(SequenceRule.org_id == current_user.organization_id)

    # 篩選條件
    if is_active is not None:
        query = query.filter(SequenceRule.is_active == is_active)

    if search:
        query = query.filter(
            or_(
                SequenceRule.rule_code.ilike(f"%{search}%"),
                SequenceRule.rule_name.ilike(f"%{search}%")
            )
        )

    # 總筆數
    total = query.count()

    # 分頁查詢
    rules = query.order_by(SequenceRule.created_at.desc()).offset(skip).limit(limit).all()

    return SequenceRuleListResponse(total=total, items=rules)


@router.get("/{rule_id}", response_model=SequenceRuleResponse, summary="取得編號規則詳情")
async def get_sequence_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("numbering_rules", "read"))
):
    """
    取得編號規則詳情

    需要權限: numbering_rules.read
    """
    rule = db.query(SequenceRule).filter(
        and_(
            SequenceRule.id == rule_id,
            SequenceRule.org_id == current_user.organization_id
        )
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="編號規則不存在"
        )

    return rule


@router.post("", response_model=SequenceRuleResponse, status_code=status.HTTP_201_CREATED, summary="建立編號規則")
async def create_sequence_rule(
    rule_data: SequenceRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("numbering_rules", "create"))
):
    """
    建立編號規則

    需要權限: numbering_rules.create
    """
    # 檢查規則代碼是否已存在
    existing = db.query(SequenceRule).filter(
        and_(
            SequenceRule.rule_code == rule_data.rule_code,
            SequenceRule.org_id == current_user.organization_id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"規則代碼已存在: {rule_data.rule_code}"
        )

    # 建立規則
    new_rule = SequenceRule(
        **rule_data.model_dump(),
        org_id=current_user.organization_id,
        created_by=current_user.id
    )

    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    logger.info(f"[NumberingRules] 建立編號規則: {new_rule.rule_code} (id={new_rule.id})")

    return new_rule


@router.put("/{rule_id}", response_model=SequenceRuleResponse, summary="更新編號規則")
async def update_sequence_rule(
    rule_id: int,
    rule_data: SequenceRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("numbering_rules", "update"))
):
    """
    更新編號規則

    需要權限: numbering_rules.update
    """
    rule = db.query(SequenceRule).filter(
        and_(
            SequenceRule.id == rule_id,
            SequenceRule.org_id == current_user.organization_id
        )
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="編號規則不存在"
        )

    # 更新欄位
    update_data = rule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    rule.updated_by = current_user.id

    db.commit()
    db.refresh(rule)

    logger.info(f"[NumberingRules] 更新編號規則: {rule.rule_code} (id={rule.id})")

    return rule


@router.delete("/{rule_id}", summary="刪除編號規則")
async def delete_sequence_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("numbering_rules", "delete"))
):
    """
    刪除編號規則

    需要權限: numbering_rules.delete
    """
    rule = db.query(SequenceRule).filter(
        and_(
            SequenceRule.id == rule_id,
            SequenceRule.org_id == current_user.organization_id
        )
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="編號規則不存在"
        )

    # 檢查是否有關聯的流水號記錄
    value_count = db.query(SequenceValue).filter(SequenceValue.rule_id == rule_id).count()
    if value_count > 0:
        logger.warning(f"[NumberingRules] 刪除編號規則將同時刪除 {value_count} 筆流水號記錄")

    db.delete(rule)
    db.commit()

    logger.info(f"[NumberingRules] 刪除編號規則: {rule.rule_code} (id={rule.id})")

    return {"message": "編號規則已刪除", "rule_id": rule_id}


# ============ 編號產生 ============

@router.post("/generate", response_model=GenerateNumberResponse, summary="產生編號")
async def generate_number(
    request: GenerateNumberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    產生編號

    此 API 不需要交易令牌,因為可能會被其他功能呼叫。
    但仍需要使用者登入驗證。
    """
    # 解析自訂日期
    custom_date = None
    if request.custom_date:
        try:
            custom_date = date.fromisoformat(request.custom_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="日期格式錯誤,應為 YYYY-MM-DD"
            )

    # 產生編號
    result = SequenceService.generate_number(
        db=db,
        rule_code=request.rule_code,
        org_id=current_user.organization_id,
        custom_date=custom_date
    )

    return GenerateNumberResponse(**result)


@router.get("/preview/{rule_code}", summary="預覽下一個編號")
async def preview_number(
    rule_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("numbering_rules", "read"))
):
    """
    預覽下一個編號 (不實際產生)

    需要權限: numbering_rules.read
    """
    result = SequenceService.preview_number(
        rule_code=rule_code,
        db=db,
        org_id=current_user.organization_id
    )

    return result


@router.post("/reset/{rule_code}", summary="重置流水號")
async def reset_sequence(
    rule_code: str,
    period: Optional[str] = Query(None, description="要重置的期間 (預設為當前期間)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("numbering_rules", "update"))
):
    """
    重置流水號

    需要權限: numbering_rules.update

    警告: 此操作會將流水號重置為 0,請謹慎使用!
    """
    result = SequenceService.reset_sequence(
        rule_code=rule_code,
        db=db,
        org_id=current_user.organization_id,
        period=period
    )

    return result


# ============ 流水號記錄查詢 ============

@router.get("/{rule_code}/values", response_model=List[SequenceValueResponse], summary="取得流水號記錄")
async def get_sequence_values(
    rule_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("numbering_rules", "read"))
):
    """
    取得指定規則的所有流水號記錄

    需要權限: numbering_rules.read
    """
    # 先取得規則
    rule = db.query(SequenceRule).filter(
        and_(
            SequenceRule.rule_code == rule_code,
            SequenceRule.org_id == current_user.organization_id
        )
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="編號規則不存在"
        )

    # 取得流水號記錄
    values = db.query(SequenceValue).filter(
        and_(
            SequenceValue.rule_id == rule.id,
            SequenceValue.org_id == current_user.organization_id
        )
    ).order_by(SequenceValue.period.desc()).all()

    return values
