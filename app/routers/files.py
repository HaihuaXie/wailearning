from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from app.attachments import save_attachment
from app.auth import get_current_active_user
from app.models import User, UserRole
from app.schemas import AttachmentUploadResponse


router = APIRouter(prefix="/api/files", tags=["文件上传"])


@router.post("/upload", response_model=AttachmentUploadResponse)
async def upload_attachment(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role not in [UserRole.ADMIN, UserRole.CLASS_TEACHER, UserRole.TEACHER]:
        raise HTTPException(status_code=403, detail="Only teachers can upload attachments.")

    uploaded = await save_attachment(file, request)
    return AttachmentUploadResponse(**uploaded)
