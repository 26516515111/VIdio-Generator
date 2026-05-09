import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

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


class DirectorRequest(BaseModel):
    text: str
    scene: str
    character: str
    direction: str
    provider: Optional[str] = None


class DirectorResponse(BaseModel):
    processed_text: str
    style_tags: str
    audio_tags: List[str]
    raw_output: str


class SceneToStyleRequest(BaseModel):
    scene: str
    provider: Optional[str] = None


class SceneToStyleResponse(BaseModel):
    style_description: str


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


@router.post("/director", response_model=DirectorResponse)
async def process_director(
    request: DirectorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """导演模式：根据角色、场景、指导生成带风格标签的文本"""
    try:
        result = await llm_service.process_director(
            text=request.text,
            scene=request.scene,
            character=request.character,
            direction=request.direction,
            user_id=current_user.id,
            db=db,
            provider=request.provider,
        )
        return result
    except Exception as e:
        logger.exception("Failed to process director mode")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/scene-to-style", response_model=SceneToStyleResponse)
async def process_scene_to_style(
    request: SceneToStyleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """将场景描述转换为TTS风格描述"""
    try:
        result = await llm_service.process_scene_to_style(
            scene=request.scene,
            user_id=current_user.id,
            db=db,
            provider=request.provider,
        )
        return {"style_description": result}
    except Exception as e:
        logger.exception("Failed to process scene to style")
        raise HTTPException(status_code=500, detail="Internal server error")
