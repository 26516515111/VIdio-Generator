import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..api.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..services.ocr_service import ocr_service

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

router = APIRouter(prefix="/api/ocr", tags=["ocr"])


class OcrResponse(BaseModel):
    text: str
    scene: str
    confidence: float


@router.post("/extract", response_model=OcrResponse)
async def extract_text_from_image(
    file: UploadFile = File(...),
    provider: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """从上传的图片中提取文字和场景信息"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_data = await file.read()
    if len(image_data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    try:
        result = await ocr_service.extract_text_from_image(
            image_data=image_data,
            user_id=current_user.id,
            db=db,
            provider=provider,
        )
        return result
    except Exception as e:
        logger.exception("Failed to extract text from image")
        raise HTTPException(status_code=500, detail="Internal server error")
