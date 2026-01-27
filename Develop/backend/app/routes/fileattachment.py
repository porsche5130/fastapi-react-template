"""
File Attachments Routes
檔案附件管理 API
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.deps import get_current_user
from app.routes.transaction import require_txn_token
from app.models.user import User
from app.models.fileattachment import FileAttachment
from app.schemas.fileattachment import (
    FileAttachmentResponse,
    FileAttachmentListResponse,
    FileAttachmentUpdate,
    FileUploadResponse,
    FileConfirmResponse
)
from app.services.file_service import FileService

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ 檔案上傳 ============

@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED, summary="上傳檔案")
async def upload_file(
    file: UploadFile = File(..., description="上傳的檔案"),
    category: str = Form(..., description="檔案分類"),
    business_type: Optional[str] = Form(None, description="業務類型"),
    related_table: Optional[str] = Form(None, description="關聯資料表"),
    related_id: Optional[int] = Form(None, description="關聯記錄 ID"),
    access_level: str = Form("private", description="存取等級"),
    is_public: bool = Form(False, description="是否公開"),
    description: Optional[str] = Form(None, description="檔案說明"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("file_attachments", "create"))
):
    """
    上傳檔案

    需要權限: file_attachments.create

    檔案會先標記為臨時檔案 (is_temp=True),
    需要呼叫 /confirm API 確認後才會轉為正式檔案。

    未確認的臨時檔案會在 24 小時後自動清理。
    """
    # 上傳檔案
    file_record = await FileService.upload_file(
        db=db,
        file=file,
        current_user=current_user,
        category=category,
        business_type=business_type,
        related_table=related_table,
        related_id=related_id,
        access_level=access_level,
        is_public=is_public,
        description=description
    )

    # 組合回應
    is_duplicate = file_record.file_metadata.get("is_duplicate", False) if file_record.file_metadata else False

    return FileUploadResponse(
        file_id=file_record.id,
        original_name=file_record.original_name,
        file_size=file_record.file_size,
        mime_type=file_record.mime_type,
        file_hash=file_record.file_hash,
        is_duplicate=is_duplicate,
        download_url=f"/api/file-attachments/download/{file_record.id}",
        thumbnail_url=f"/api/file-attachments/thumbnail/{file_record.id}" if file_record.thumbnail_path else None,
        is_temp=file_record.is_temp,
        expires_at=None  # 可以加上過期時間邏輯
    )


@router.post("/{file_id}/confirm", response_model=FileConfirmResponse, summary="確認檔案")
async def confirm_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("file_attachments", "create"))
):
    """
    確認檔案 (將臨時檔案轉為正式檔案)

    需要權限: file_attachments.create
    """
    file_record = FileService.confirm_file(
        db=db,
        file_id=file_id,
        current_user=current_user
    )

    return FileConfirmResponse(
        message="檔案已確認",
        file_id=file_record.id,
        confirmed_at=file_record.confirmed_at
    )


# ============ 檔案查詢 ============

@router.get("", response_model=FileAttachmentListResponse, summary="取得檔案列表")
async def get_files(
    skip: int = Query(0, ge=0, description="跳過筆數"),
    limit: int = Query(20, ge=1, le=100, description="每頁筆數"),
    category: Optional[str] = Query(None, description="檔案分類"),
    business_type: Optional[str] = Query(None, description="業務類型"),
    related_table: Optional[str] = Query(None, description="關聯資料表"),
    related_id: Optional[int] = Query(None, description="關聯記錄 ID"),
    is_temp: Optional[bool] = Query(None, description="是否為臨時檔案"),
    search: Optional[str] = Query(None, description="搜尋關鍵字 (檔案名稱)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("file_attachments", "read"))
):
    """
    取得檔案列表

    需要權限: file_attachments.read
    """
    query = db.query(FileAttachment).filter(FileAttachment.org_id == current_user.organization_id)

    # 篩選條件
    if category:
        query = query.filter(FileAttachment.category == category)

    if business_type:
        query = query.filter(FileAttachment.business_type == business_type)

    if related_table:
        query = query.filter(FileAttachment.related_table == related_table)

    if related_id:
        query = query.filter(FileAttachment.related_id == related_id)

    if is_temp is not None:
        query = query.filter(FileAttachment.is_temp == is_temp)

    if search:
        query = query.filter(FileAttachment.original_name.ilike(f"%{search}%"))

    # 總筆數
    total = query.count()

    # 分頁查詢
    files = query.order_by(FileAttachment.created_at.desc()).offset(skip).limit(limit).all()

    # 加上 download_url
    for file in files:
        file.download_url = f"/api/file-attachments/download/{file.id}"
        if file.thumbnail_path:
            file.thumbnail_url = f"/api/file-attachments/thumbnail/{file.id}"

    return FileAttachmentListResponse(total=total, items=files)


@router.get("/{file_id}", response_model=FileAttachmentResponse, summary="取得檔案詳情")
async def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("file_attachments", "read"))
):
    """
    取得檔案詳情

    需要權限: file_attachments.read
    """
    file_record = db.query(FileAttachment).filter(
        and_(
            FileAttachment.id == file_id,
            FileAttachment.org_id == current_user.organization_id
        )
    ).first()

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="檔案不存在"
        )

    # 檢查存取權限
    if not FileService.check_file_access(file_record, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限存取此檔案"
        )

    # 加上 URL
    file_record.download_url = f"/api/file-attachments/download/{file_record.id}"
    if file_record.thumbnail_path:
        file_record.thumbnail_url = f"/api/file-attachments/thumbnail/{file_record.id}"

    return file_record


# ============ 檔案更新 ============

@router.put("/{file_id}", response_model=FileAttachmentResponse, summary="更新檔案資訊")
async def update_file(
    file_id: int,
    file_data: FileAttachmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("file_attachments", "update"))
):
    """
    更新檔案資訊 (不包含檔案本身,僅更新 metadata)

    需要權限: file_attachments.update
    """
    file_record = db.query(FileAttachment).filter(
        and_(
            FileAttachment.id == file_id,
            FileAttachment.org_id == current_user.organization_id
        )
    ).first()

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="檔案不存在"
        )

    # 檢查權限 (只有上傳者可以更新)
    if file_record.uploaded_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限更新此檔案"
        )

    # 更新欄位
    update_data = file_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(file_record, field, value)

    db.commit()
    db.refresh(file_record)

    logger.info(f"[FileAttachments] 更新檔案資訊: {file_record.original_name} (id={file_record.id})")

    # 加上 URL
    file_record.download_url = f"/api/file-attachments/download/{file_record.id}"
    if file_record.thumbnail_path:
        file_record.thumbnail_url = f"/api/file-attachments/thumbnail/{file_record.id}"

    return file_record


# ============ 檔案刪除 ============

@router.delete("/{file_id}", summary="刪除檔案")
async def delete_file(
    file_id: int,
    physical_delete: bool = Query(False, description="是否實體刪除檔案"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("file_attachments", "delete"))
):
    """
    刪除檔案

    需要權限: file_attachments.delete

    - physical_delete=False: 只刪除資料庫記錄,保留實體檔案 (預設)
    - physical_delete=True: 同時刪除實體檔案
    """
    result = FileService.delete_file(
        db=db,
        file_id=file_id,
        current_user=current_user,
        physical_delete=physical_delete
    )

    return result


# ============ 檔案下載 ============

@router.get("/download/{file_id}", summary="下載檔案")
async def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下載檔案

    此 API 不需要交易令牌,但需要登入驗證。
    會根據檔案的 access_level 檢查存取權限。
    """
    file_record = db.query(FileAttachment).filter(FileAttachment.id == file_id).first()

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="檔案不存在"
        )

    # 檢查存取權限
    if not FileService.check_file_access(file_record, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限存取此檔案"
        )

    # 取得檔案路徑
    file_path = FileService.get_file_path(file_record)

    if not file_path.exists():
        logger.error(f"[FileAttachments] 檔案實體不存在: {file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="檔案實體不存在"
        )

    # 更新下載統計
    file_record.download_count += 1
    file_record.last_downloaded_at = db.func.current_timestamp()
    db.commit()

    # 記錄下載日誌
    from app.services.userlog_service import UserLogService
    UserLogService.create_log(
        db=db,
        user_id=current_user.id,
        func_code="file_attachments",
        action="download",
        ip_address=None,  # 可以從 Request 取得
        details={
            "file_id": file_id,
            "file_name": file_record.original_name,
            "file_size": file_record.file_size
        }
    )

    logger.info(f"[FileAttachments] 下載檔案: {file_record.original_name} (id={file_id}, user={current_user.id})")

    # 設定 Cache-Control
    cache_control = "public, max-age=86400" if file_record.is_public else "private, no-cache, no-store, must-revalidate"

    # 回傳檔案
    return FileResponse(
        path=file_path,
        filename=file_record.original_name,
        media_type=file_record.mime_type,
        headers={
            "Cache-Control": cache_control,
            "Content-Disposition": f'attachment; filename="{file_record.original_name}"'
        }
    )


# ============ 清理臨時檔案 ============

@router.post("/cleanup", summary="清理過期臨時檔案")
async def cleanup_temp_files(
    hours: int = Query(24, ge=1, le=168, description="超過幾小時未確認的臨時檔案將被刪除"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_txn_token("file_attachments", "delete"))
):
    """
    清理過期的臨時檔案

    需要權限: file_attachments.delete

    預設清理 24 小時前的臨時檔案,最多可設定 168 小時 (7 天)
    """
    count = FileService.cleanup_temp_files(db=db, hours=hours)

    return {
        "message": f"已清理 {count} 個過期臨時檔案",
        "count": count,
        "hours": hours
    }
