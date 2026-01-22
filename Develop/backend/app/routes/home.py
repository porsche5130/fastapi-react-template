"""
Home Routes
系統首頁 API 路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/stats", summary="取得首頁統計資訊")
async def get_home_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, int]:
    """
    取得首頁統計資訊
    - 專案總數
    - 進行中專案
    - 待處理任務
    - 已完成任務
    """
    # TODO: 實作實際的統計邏輯
    return {
        "totalProjects": 0,
        "activeProjects": 0,
        "pendingTasks": 0,
        "completedTasks": 0
    }


@router.get("/activities", summary="取得最近活動記錄")
async def get_recent_activities(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    取得最近活動記錄
    """
    # TODO: 從 user_logs 取得最近的活動記錄
    return []


@router.get("/quick-links", summary="取得快速連結")
async def get_quick_links(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, str]]:
    """
    取得使用者的快速連結
    """
    # TODO: 根據使用者權限返回可用的快速連結
    return []
