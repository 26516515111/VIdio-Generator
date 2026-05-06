import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from sqlalchemy.orm import Session

from ..config import settings
from ..services.user_service import user_service


class TtsService:
    async def text_to_speech(
        self,
        text: str,
        voice: str = "default",
        emotion: str = "neutral",
        user_id: int = None,
        db: Session = None,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """将文字转换为语音"""
        # 获取用户的API密钥
        if db and user_id:
            if provider:
                api_key = user_service.get_user_api_keys(
                    db, user_id, service_type="tts"
                )
                api_key = next((k for k in api_key if k.provider == provider), None)
            else:
                api_key = user_service.get_default_api_key(db, user_id, "tts")

            if api_key:
                api_key_value = api_key.api_key
                provider = api_key.provider
            else:
                api_key_value = settings.XIAOMI_API_KEY
                provider = "xiaomi"
        else:
            api_key_value = settings.XIAOMI_API_KEY
            provider = "xiaomi"

        # 根据提供商调用不同的API
        if provider == "xiaomi":
            return await self._call_xiaomi_tts(text, voice, emotion, api_key_value)
        elif provider == "tencent":
            return await self._call_tencent_tts(text, voice, emotion, api_key_value)
        else:
            raise ValueError(f"Unsupported TTS provider: {provider}")

    async def _call_xiaomi_tts(
        self, text: str, voice: str, emotion: str, api_key: str
    ) -> Dict[str, Any]:
        """调用小米MiMo TTS"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.XIAOMI_API_BASE}/tts/synthesize",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "text": text,
                    "voice": voice,
                    "emotion": emotion,
                    "format": "mp3",
                },
                timeout=60.0,
            )

            if response.status_code != 200:
                raise Exception(f"Xiaomi TTS API error: {response.text}")

            # 保存音频文件
            audio_data = response.content
            audio_filename = f"{uuid.uuid4()}.mp3"
            audio_path = Path("data/audio") / audio_filename
            audio_path.parent.mkdir(parents=True, exist_ok=True)

            with open(audio_path, "wb") as f:
                f.write(audio_data)

            return {
                "audio_path": str(audio_path),
                "audio_url": f"/api/tts/audio/{audio_filename}",
                "duration": 0,
                "format": "mp3",
            }

    async def _call_tencent_tts(
        self, text: str, voice: str, emotion: str, api_key: str
    ) -> Dict[str, Any]:
        """调用腾讯云TTS"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://tts.tencentcloudapi.com",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={"Text": text, "VoiceType": voice, "Emotion": emotion},
                timeout=60.0,
            )

            if response.status_code != 200:
                raise Exception(f"Tencent TTS API error: {response.text}")

            # 保存音频文件
            audio_data = response.content
            audio_filename = f"{uuid.uuid4()}.mp3"
            audio_path = Path("data/audio") / audio_filename
            audio_path.parent.mkdir(parents=True, exist_ok=True)

            with open(audio_path, "wb") as f:
                f.write(audio_data)

            return {
                "audio_path": str(audio_path),
                "audio_url": f"/api/tts/audio/{audio_filename}",
                "duration": 0,
                "format": "mp3",
            }


tts_service = TtsService()
