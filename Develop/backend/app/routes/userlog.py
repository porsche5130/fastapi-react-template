"""
UserLog Routes
使用者日誌 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, or_
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.userlog import UserLog
from app.models.user_detail import UserDetail
from app.models.sysfunction import SysFunction
from app.schemas.userlog import UserLogResponse, UserLogCreate, UserLogCreateByFrontend
from app.services.userlog_service import UserLogService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[UserLogResponse], summary="取得使用者日誌列表")
async def get_user_logs(
    user_detail_id: Optional[int] = Query(None, description="作業人員ID"),
    sysfunction_id: Optional[int] = Query(None, description="作業功能ID"),
    module_item: Optional[str] = Query(None, description="模組項目"),
    data_id: Optional[int] = Query(None, description="資料序號"),
    start_date: Optional[datetime] = Query(None, description="開始日期時間"),
    end_date: Optional[datetime] = Query(None, description="結束日期時間"),
    has_error: Optional[bool] = Query(None, description="是否有錯誤"),
    skip: int = Query(0, ge=0, description="略過筆數"),
    limit: int = Query(100, ge=1, le=1000, description="取得筆數"),
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得使用者日誌列表（支援多條件查詢）
    """

    # 建立查詢條件
    conditions = []
    if user_detail_id:
        conditions.append(UserLog.user_detail_id == user_detail_id)
    if sysfunction_id:
        conditions.append(UserLog.sysfunction_id == sysfunction_id)
    if module_item:
        conditions.append(UserLog.module_item == module_item)
    if data_id:
        conditions.append(UserLog.data_id == data_id)
    if start_date:
        conditions.append(UserLog.action_at >= start_date)
    if end_date:
        conditions.append(UserLog.action_at <= end_date)
    if has_error is not None:
        if has_error:
            conditions.append(UserLog.err_detail.isnot(None))
        else:
            conditions.append(UserLog.err_detail.is_(None))

    # 查詢（使用 joinedload 載入關聯資料）
    query = db.query(UserLog).options(
        joinedload(UserLog.user),
        joinedload(UserLog.function)
    )
    if conditions:
        query = query.filter(and_(*conditions))

    # 排序並分頁
    logs = query.order_by(desc(UserLog.action_at)).offset(skip).limit(limit).all()

    # 建立回應，包含使用者名稱和功能名稱
    result = []
    for log in logs:
        log_response = UserLogResponse(
            id=log.id,
            user_detail_id=log.user_detail_id,
            sysfunction_id=log.sysfunction_id,
            module_item=log.module_item,
            session_id=log.session_id,
            data_id=log.data_id,
            look_data=log.look_data or {},
            change_data=log.change_data or {},
            action_at=log.action_at,
            err_detail=log.err_detail,
            user_name=log.user.username if log.user else None,
            function_name=log.function.func_cname if log.function else None
        )
        result.append(log_response)

    return result


@router.get("/{log_id}", response_model=UserLogResponse, summary="取得單筆日誌")
async def get_user_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    根據 ID 取得單筆日誌
    """
    log = db.query(UserLog).options(
        joinedload(UserLog.user),
        joinedload(UserLog.function)
    ).filter(UserLog.id == log_id).first()

    if not log:
        raise HTTPException(status_code=404, detail="日誌不存在")

    # 記錄讀取日誌

    return UserLogResponse(
        id=log.id,
        user_detail_id=log.user_detail_id,
        sysfunction_id=log.sysfunction_id,
        module_item=log.module_item,
        session_id=log.session_id,
        data_id=log.data_id,
        look_data=log.look_data or {},
        change_data=log.change_data or {},
        action_at=log.action_at,
        err_detail=log.err_detail,
        user_name=log.user.username if log.user else None,
        function_name=log.function.func_cname if log.function else None
    )


@router.get("/user/{user_id}", response_model=List[UserLogResponse], summary="取得特定使用者的日誌")
async def get_user_logs_by_user(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得特定使用者的所有日誌
    """
    logs = db.query(UserLog).options(
        joinedload(UserLog.user),
        joinedload(UserLog.function)
    ).filter(
        UserLog.user_detail_id == user_id
    ).order_by(desc(UserLog.action_at)).offset(skip).limit(limit).all()

    result = []
    for log in logs:
        log_response = UserLogResponse(
            id=log.id,
            user_detail_id=log.user_detail_id,
            sysfunction_id=log.sysfunction_id,
            module_item=log.module_item,
            session_id=log.session_id,
            data_id=log.data_id,
            look_data=log.look_data or {},
            change_data=log.change_data or {},
            action_at=log.action_at,
            err_detail=log.err_detail,
            user_name=log.user.username if log.user else None,
            function_name=log.function.func_cname if log.function else None
        )
        result.append(log_response)

    return result


@router.get("/function/{function_id}", response_model=List[UserLogResponse], summary="取得特定功能的日誌")
async def get_user_logs_by_function(
    function_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    取得特定功能的所有日誌
    """
    logs = db.query(UserLog).options(
        joinedload(UserLog.user),
        joinedload(UserLog.function)
    ).filter(
        UserLog.sysfunction_id == function_id
    ).order_by(desc(UserLog.action_at)).offset(skip).limit(limit).all()

    result = []
    for log in logs:
        log_response = UserLogResponse(
            id=log.id,
            user_detail_id=log.user_detail_id,
            sysfunction_id=log.sysfunction_id,
            module_item=log.module_item,
            session_id=log.session_id,
            data_id=log.data_id,
            look_data=log.look_data or {},
            change_data=log.change_data or {},
            action_at=log.action_at,
            err_detail=log.err_detail,
            user_name=log.user.username if log.user else None,
            function_name=log.function.func_cname if log.function else None
        )
        result.append(log_response)

    return result


@router.post("/log", response_model=UserLogResponse, summary="建立日誌記錄（前端呼叫）")
async def create_user_log_from_frontend(
    log: UserLogCreateByFrontend,
    db: Session = Depends(get_db),
    current_user: UserDetail = Depends(get_current_user)
):
    """
    由前端主動呼叫建立日誌記錄
    用於記錄使用者的各種操作行為（View, Read, Create, Update, Delete 等）

    前端不需要提供 user_detail_id 和 session_id，由後端自動填入
    data_id 優先使用前端提供的值，若無則自動從 change_data 或 look_data 中提取
    """
    # 自動提取 data_id（優先前端提供，其次從 change_data，最後從 look_data）
    data_id = log.data_id
    if data_id is None and log.change_data and 'id' in log.change_data:
        data_id = log.change_data.get('id')
        logger.info(f"[UserLog] Auto-extracted data_id from change_data: {data_id}")
    elif data_id is None and log.look_data and 'id' in log.look_data:
        data_id = log.look_data.get('id')
        logger.info(f"[UserLog] Auto-extracted data_id from look_data: {data_id}")

    # 使用當前登入使用者的 ID 和 session_id
    new_log = UserLog(
        user_detail_id=current_user.id,
        session_id=current_user.current_session_id if hasattr(current_user, 'current_session_id') else None,
        sysfunction_id=log.sysfunction_id,
        module_item=log.module_item,
        data_id=data_id,
        look_data=log.look_data or {},
        change_data=log.change_data or {},
        action_at=datetime.now(),
        err_detail=log.err_detail
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    # 取得功能名稱
    function = db.query(SysFunction).filter(SysFunction.id == log.sysfunction_id).first()

    return UserLogResponse(
        id=new_log.id,
        user_detail_id=new_log.user_detail_id,
        sysfunction_id=new_log.sysfunction_id,
        module_item=new_log.module_item,
        session_id=new_log.session_id,
        data_id=new_log.data_id,
        look_data=new_log.look_data or {},
        change_data=new_log.change_data or {},
        action_at=new_log.action_at,
        err_detail=new_log.err_detail,
        user_name=current_user.username,
        function_name=function.func_cname if function else None
    )
