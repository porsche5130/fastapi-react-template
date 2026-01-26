"""
File Service
檔案處理服務
"""

import logging
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, BinaryIO
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status, UploadFile

from app.models.fileattachment import FileAttachment
from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


class FileService:
    """檔案處理服務類別"""

    @staticmethod
    def calculate_file_hash(file: BinaryIO) -> str:
        """
        計算檔案的 SHA-256 雜湊值

        Args:
            file: 檔案物件

        Returns:
            str: SHA-256 雜湊值 (hex)
        """
        sha256_hash = hashlib.sha256()
        # 重置檔案指標到開頭
        file.seek(0)
        # 分塊讀取檔案
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)
        # 重置檔案指標
        file.seek(0)
        return sha256_hash.hexdigest()

    @staticmethod
    def check_duplicate(db: Session, file_hash: str, org_id: int) -> Optional[FileAttachment]:
        """
        檢查是否有重複檔案

        Args:
            db: 資料庫 Session
            file_hash: 檔案雜湊
            org_id: 組織 ID

        Returns:
            FileAttachment or None: 如果找到重複檔案則回傳,否則回傳 None
        """
        return db.query(FileAttachment).filter(
            and_(
                FileAttachment.file_hash == file_hash,
                FileAttachment.org_id == org_id,
                FileAttachment.is_temp == False
            )
        ).first()

    @staticmethod
    async def upload_file(
        db: Session,
        file: UploadFile,
        current_user: User,
        category: str,
        business_type: Optional[str] = None,
        related_table: Optional[str] = None,
        related_id: Optional[int] = None,
        access_level: str = "private",
        is_public: bool = False,
        allowed_roles: Optional[list] = None,
        allowed_users: Optional[list] = None,
        description: Optional[str] = None,
        tags: Optional[list] = None
    ) -> FileAttachment:
        """
        上傳檔案

        Args:
            db: 資料庫 Session
            file: 上傳的檔案
            current_user: 當前使用者
            category: 檔案分類
            其他參數: 檔案屬性

        Returns:
            FileAttachment: 檔案記錄

        Raises:
            HTTPException: 檔案過大、類型不允許等錯誤
        """
        # 1. 驗證檔案大小
        file.file.seek(0, 2)  # 移到檔案結尾
        file_size = file.file.tell()  # 取得檔案大小
        file.file.seek(0)  # 重置到開頭

        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"檔案大小超過限制 ({settings.MAX_UPLOAD_SIZE_MB} MB)"
            )

        # 2. 驗證檔案類型
        mime_type = file.content_type
        allowed_types = []

        if category == "image":
            allowed_types = settings.ALLOWED_IMAGE_TYPES
        elif category == "document":
            allowed_types = settings.ALLOWED_DOCUMENT_TYPES
        else:
            # 其他類型暫時允許所有
            allowed_types = None

        if allowed_types and mime_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"不支援的檔案類型: {mime_type}"
            )

        # 3. 計算檔案雜湊
        file_hash = FileService.calculate_file_hash(file.file)

        # 4. 檢查重複檔案
        org_id = current_user.organization_id
        duplicate = FileService.check_duplicate(db, file_hash, org_id)
        is_duplicate = duplicate is not None

        # 5. 產生儲存路徑 (年/月/hash[:2]/hash)
        now = datetime.now()
        year_month = now.strftime("%Y/%m")
        hash_prefix = file_hash[:2]
        storage_dir = settings.uploads_path / year_month / hash_prefix
        storage_dir.mkdir(parents=True, exist_ok=True)

        # 檔案名稱使用 hash + 原始副檔名
        file_ext = Path(file.filename).suffix
        storage_filename = f"{file_hash}{file_ext}"
        storage_path_full = storage_dir / storage_filename

        # 相對路徑 (儲存到資料庫)
        storage_path_relative = f"{year_month}/{hash_prefix}/{storage_filename}"

        # 6. 儲存檔案 (如果不是重複檔案)
        if not is_duplicate:
            with open(storage_path_full, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        # 7. 建立資料庫記錄
        file_record = FileAttachment(
            original_name=file.filename,
            storage_path=storage_path_relative,
            file_size=file_size,
            mime_type=mime_type,
            file_hash=file_hash,
            category=category,
            business_type=business_type,
            related_table=related_table,
            related_id=related_id,
            access_level=access_level,
            is_public=is_public,
            allowed_roles=allowed_roles,
            allowed_users=allowed_users,
            is_temp=True,  # 預設為臨時檔案
            description=description,
            tags=tags,
            org_id=org_id,
            uploaded_by=current_user.id,
            file_metadata={"is_duplicate": is_duplicate, "duplicate_id": duplicate.id if duplicate else None}
        )

        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        logger.info(
            f"[File] 上傳檔案: {file.filename} "
            f"(id={file_record.id}, size={file_size}, hash={file_hash[:8]}..., duplicate={is_duplicate})"
        )

        return file_record

    @staticmethod
    def confirm_file(db: Session, file_id: int, current_user: User) -> FileAttachment:
        """
        確認檔案 (將臨時檔案轉為正式檔案)

        Args:
            db: 資料庫 Session
            file_id: 檔案 ID
            current_user: 當前使用者

        Returns:
            FileAttachment: 確認後的檔案記錄

        Raises:
            HTTPException: 檔案不存在、無權限等錯誤
        """
        file_record = db.query(FileAttachment).filter(FileAttachment.id == file_id).first()

        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="檔案不存在"
            )

        # 檢查權限 (只有上傳者可以確認)
        if file_record.uploaded_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限確認此檔案"
            )

        if not file_record.is_temp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="檔案已經確認過了"
            )

        # 確認檔案
        file_record.is_temp = False
        file_record.confirmed_at = datetime.now()
        file_record.updated_at = datetime.now()

        db.commit()
        db.refresh(file_record)

        logger.info(f"[File] 確認檔案: id={file_id}, name={file_record.original_name}")

        return file_record

    @staticmethod
    def get_file_path(file_record: FileAttachment) -> Path:
        """
        取得檔案完整路徑

        Args:
            file_record: 檔案記錄

        Returns:
            Path: 檔案完整路徑
        """
        return settings.uploads_path / file_record.storage_path

    @staticmethod
    def check_file_access(file_record: FileAttachment, current_user: User, db: Session) -> bool:
        """
        檢查使用者是否有權限存取檔案

        Args:
            file_record: 檔案記錄
            current_user: 當前使用者
            db: 資料庫 Session

        Returns:
            bool: True 表示有權限, False 表示無權限
        """
        # 1. 公開檔案 → 直接通過
        if file_record.is_public:
            return True

        # 2. 檔案上傳者 → 直接通過
        if file_record.uploaded_by == current_user.id:
            return True

        # 3. Private (私人) → 只有上傳者可存取
        if file_record.access_level == "private":
            return False

        # 4. Restricted (限制) → 檢查角色或明確授權
        if file_record.access_level == "restricted":
            # 檢查使用者是否在允許列表中
            if file_record.allowed_users and current_user.id in file_record.allowed_users:
                return True

            # 檢查使用者角色是否在允許列表中
            if file_record.allowed_roles:
                from app.models.userrole import UserRole
                user_roles = db.query(UserRole.role_name).filter(
                    UserRole.user_id == current_user.id
                ).all()
                user_role_names = [role[0] for role in user_roles]

                for allowed_role in file_record.allowed_roles:
                    if allowed_role in user_role_names:
                        return True

            return False

        return False

    @staticmethod
    def delete_file(db: Session, file_id: int, current_user: User, physical_delete: bool = False) -> dict:
        """
        刪除檔案

        Args:
            db: 資料庫 Session
            file_id: 檔案 ID
            current_user: 當前使用者
            physical_delete: 是否實體刪除檔案 (預設 False,只刪除記錄)

        Returns:
            dict: 刪除結果

        Raises:
            HTTPException: 檔案不存在、無權限等錯誤
        """
        file_record = db.query(FileAttachment).filter(FileAttachment.id == file_id).first()

        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="檔案不存在"
            )

        # 檢查權限 (只有上傳者可以刪除)
        if file_record.uploaded_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="無權限刪除此檔案"
            )

        # 實體刪除檔案
        if physical_delete:
            file_path = FileService.get_file_path(file_record)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"[File] 實體刪除檔案: {file_path}")

        # 刪除資料庫記錄
        db.delete(file_record)
        db.commit()

        logger.info(f"[File] 刪除檔案記錄: id={file_id}, name={file_record.original_name}")

        return {
            "message": "檔案已刪除",
            "file_id": file_id,
            "physical_deleted": physical_delete
        }

    @staticmethod
    def cleanup_temp_files(db: Session, hours: int = 24) -> int:
        """
        清理過期的臨時檔案

        Args:
            db: 資料庫 Session
            hours: 超過幾小時未確認的臨時檔案將被刪除 (預設 24 小時)

        Returns:
            int: 清理的檔案數量
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # 找出過期的臨時檔案
        expired_files = db.query(FileAttachment).filter(
            and_(
                FileAttachment.is_temp == True,
                FileAttachment.created_at < cutoff_time
            )
        ).all()

        count = 0
        for file_record in expired_files:
            # 實體刪除檔案
            file_path = FileService.get_file_path(file_record)
            if file_path.exists():
                file_path.unlink()

            # 刪除記錄
            db.delete(file_record)
            count += 1

        db.commit()

        if count > 0:
            logger.info(f"[File] 清理過期臨時檔案: {count} 個")

        return count
