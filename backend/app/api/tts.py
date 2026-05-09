import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..api.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..services.tts_service import tts_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tts", tags=["tts"])


class TtsRequest(BaseModel):
    text: str
    voice: str = "default"
    emotion: str = "neutral"
    style_tags: Optional[str] = None
    scene: Optional[str] = None
    character: Optional[str] = None
    direction: Optional[str] = None
    custom_voice_type: Optional[str] = None  # "voicedesign" or "voiceclone"
    custom_voice_data: Optional[str] = None  # Text description or base64 audio
    provider: Optional[str] = None


class TtsResponse(BaseModel):
    audio_url: str
    duration: float
    format: str


@router.post("/synthesize", response_model=TtsResponse)
async def synthesize_speech(
    request: TtsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """将文字转换为语音"""
    try:
        result = await tts_service.text_to_speech(
            text=request.text,
            voice=request.voice,
            emotion=request.emotion,
            user_id=current_user.id,
            db=db,
            provider=request.provider,
            style_tags=request.style_tags,
            scene=request.scene,
            character=request.character,
            direction=request.direction,
            custom_voice_type=request.custom_voice_type,
            custom_voice_data=request.custom_voice_data,
        )
        return result
    except Exception as e:
        logger.exception("Failed to synthesize speech")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    """获取生成的音频文件"""
    # Prevent path traversal
    safe_name = Path(filename).name
    audio_path = Path("data/audio") / safe_name
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    # 根据文件扩展名设置正确的 media_type
    if safe_name.endswith(".wav"):
        media_type = "audio/wav"
    else:
        media_type = "audio/mpeg"

    return FileResponse(
        path=str(audio_path), media_type=media_type, filename=safe_name
    )
