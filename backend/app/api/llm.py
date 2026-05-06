import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from ..api.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..services.llm_service import llm_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["llm"])


class TextProcessRequest(BaseModel):
    text: str
    scene: str
    emotion: Optional[str] = None
    processing_type: Optional[str] = None
    provider: Optional[str] = None


class TextProcessResponse(BaseModel):
    processed_text: str
    detected_emotion: str
    processing_type: str


@router.post("/process", response_model=TextProcessResponse)
async def process_text(
    request: TextProcessRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """使用大模型处理文字"""
    try:
        result = await llm_service.process_text(
            text=request.text,
            scene=request.scene,
            emotion=request.emotion,
            processing_type=request.processing_type,
            user_id=current_user.id,
            db=db,
            provider=request.provider,
        )
        return result
    except Exception as e:
        logger.exception("Failed to process text")
        raise HTTPException(status_code=500, detail="Internal server error")
