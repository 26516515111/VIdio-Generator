import uuid
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from sqlalchemy.orm import Session

from ..config import settings, _get_app_dir
from ..services.user_service import user_service

logger = logging.getLogger(__name__)


class TtsService:
    async def text_to_speech(
        self,
        text: str,
        voice: str = "default",
        emotion: str = "neutral",
        user_id: int = None,
        db: Session = None,
        provider: Optional[str] = None,
        style_tags: Optional[str] = None,
        scene: Optional[str] = None,
        character: Optional[str] = None,
        direction: Optional[str] = None,
        custom_voice_type: Optional[str] = None,
        custom_voice_data: Optional[str] = None,
    ) -> Dict[str, Any]:
        """将文字转换为语音"""
        # 获取用户的API密钥
        base_url = None
        if db and user_id:
            if provider:
                api_keys = user_service.get_user_api_keys(
                    db, user_id, service_type="tts"
                )
                api_key = next((k for k in api_keys if k.provider == provider), None)
            else:
                # 先查找默认的，如果没有则查找任意一个
                api_key = user_service.get_default_api_key(db, user_id, "tts")
                if not api_key:
                    api_keys = user_service.get_user_api_keys(db, user_id, service_type="tts")
                    api_key = api_keys[0] if api_keys else None

            if api_key:
                api_key_value = api_key.api_key
                provider = api_key.provider
                base_url = api_key.base_url
            else:
                api_key_value = settings.XIAOMI_TOKENPLAN_API_KEY
                provider = "xiaomi-tokenplan"
                base_url = settings.XIAOMI_TOKENPLAN_API_BASE
        else:
            api_key_value = settings.XIAOMI_TOKENPLAN_API_KEY
            provider = "xiaomi-tokenplan"
            base_url = settings.XIAOMI_TOKENPLAN_API_BASE

        # 根据提供商调用不同的API
        if not api_key_value:
            raise Exception("未找到TTS API密钥，请先在个人中心配置API密钥")
        
        if provider in ["xiaomi", "xiaomi-tokenplan"]:
            return await self._call_xiaomi_tts(text, voice, emotion, api_key_value, base_url, style_tags, scene, character, direction, custom_voice_type, custom_voice_data)
        elif provider == "tencent":
            return await self._call_tencent_tts(text, voice, emotion, api_key_value, base_url)
        else:
            raise ValueError(f"Unsupported TTS provider: {provider}")

    async def _call_xiaomi_tts(
        self, text: str, voice: str, emotion: str, api_key: str, base_url: Optional[str] = None, style_tags: Optional[str] = None,
        scene: Optional[str] = None, character: Optional[str] = None, direction: Optional[str] = None,
        custom_voice_type: Optional[str] = None, custom_voice_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """调用小米MiMo TTS (使用chat/completions端点)"""
        if not api_key:
            raise Exception("请先配置小米 Token Plan API 密钥")
        
        url = f"{base_url or settings.XIAOMI_API_BASE}/chat/completions"
        
        # ===== 1. Determine model and voice =====
        has_custom_voice = custom_voice_type is not None and custom_voice_data is not None
        
        if has_custom_voice:
            if custom_voice_type == "voiceclone":
                # Upload audio has higher priority
                model = "mimo-v2.5-tts-voiceclone"
                voice_for_audio = f"data:audio/mpeg;base64,{custom_voice_data}"
                logger.info(f"Using voice clone mode with uploaded audio (data length: {len(custom_voice_data)} chars)")
            else:
                # Text description
                model = "mimo-v2.5-tts-voicedesign"
                voice_for_audio = None  # No voice field in audio
                logger.info(f"Using voice design mode with description: {custom_voice_data[:50]}...")
        else:
            # Standard voice
            model = "mimo-v2.5-tts"
            voice_map = {
                "default": "mimo_default",
                "mimo_default": "mimo_default",
                "default_zh": "default_zh",
                "default_en": "default_en",
                "冰糖": "冰糖",
                "茉莉": "茉莉",
                "苏打": "苏打",
                "白桦": "白桦",
                "Mia": "Mia",
                "Chloe": "Chloe",
                "Milo": "Milo",
                "Dean": "Dean",
            }
            voice_for_audio = voice_map.get(voice, "mimo_default")
            logger.info(f"Using standard voice: {voice_for_audio}")
        
        # ===== 2. Build user message =====
        user_content = ""
        
        if character:
            # Director mode: character defines the voice style
            user_content = character
            # If custom voice text description, append to character
            if has_custom_voice and custom_voice_type == "voicedesign":
                user_content = f"{custom_voice_data}\n\n{character}"
        else:
            # Normal mode
            parts = []
            # Add custom voice description if text mode
            if has_custom_voice and custom_voice_type == "voicedesign":
                parts.append(custom_voice_data)
            # Add scene/emotion
            if scene:
                parts.append(f"Scene: {scene}. Adjust tone and style accordingly.")
            elif emotion and emotion != "neutral":
                emotion_descriptions = {
                    "happy": "Bright, cheerful, upbeat tone. Fast pace, rising pitch.",
                    "sad": "Soft, melancholic tone. Slow pace, low pitch.",
                    "angry": "Intense, forceful tone. Sharp delivery.",
                    "excited": "Energetic, enthusiastic tone. Fast pace.",
                    "neutral": "Calm, natural tone. Moderate pace.",
                }
                parts.append(emotion_descriptions.get(emotion, ""))
            user_content = "\n\n".join(parts)
        
        # ===== 3. Build assistant message =====
        assistant_content = text
        if style_tags:
            assistant_content = f"({style_tags}){text}"
        elif emotion and emotion != "neutral" and not has_custom_voice:
            assistant_content = f"({emotion}){text}"
        
        messages = [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content}
        ]
        
        # ===== 4. Build audio config =====
        audio_config = {"format": "wav"}
        if voice_for_audio is not None:
            audio_config["voice"] = voice_for_audio
        
        # ===== 5. Call API =====
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "audio": audio_config,
                },
                timeout=180.0,
            )

            if response.status_code != 200:
                logger.error(f"TTS API failed with status {response.status_code}: {response.text}")
                raise Exception(f"Xiaomi TTS API error: {response.text}")

            result = response.json()
            
            # Parse audio data
            audio_data = None
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {})
                audio_info = message.get("audio", {})
                audio_data = audio_info.get("data")
            
            if not audio_data:
                logger.error("TTS returned no audio data")
                raise Exception("TTS返回无音频数据")
            
            # Decode and save
            import base64
            audio_bytes = base64.b64decode(audio_data)
            
            audio_filename = f"{uuid.uuid4()}.wav"
            audio_path = _get_app_dir() / "data" / "audio" / audio_filename
            audio_path.parent.mkdir(parents=True, exist_ok=True)

            with open(audio_path, "wb") as f:
                f.write(audio_bytes)
            
            # Log success with custom voice details
            if has_custom_voice:
                if custom_voice_type == "voiceclone":
                    logger.info(f"Voice clone TTS succeeded. Audio saved: {audio_filename} ({len(audio_bytes)} bytes)")
                else:
                    logger.info(f"Voice design TTS succeeded. Audio saved: {audio_filename} ({len(audio_bytes)} bytes)")
            else:
                logger.info(f"Standard TTS succeeded. Voice: {voice_for_audio}, Audio saved: {audio_filename} ({len(audio_bytes)} bytes)")

            return {
                "audio_path": str(audio_path),
                "audio_url": f"/api/tts/audio/{audio_filename}",
                "duration": 0,
                "format": "wav",
            }

    async def _call_tencent_tts(
        self, text: str, voice: str, emotion: str, api_key: str, base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """调用腾讯云TTS"""
        url = base_url or settings.TENCENT_TTS_BASE_URL
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
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
            audio_path = _get_app_dir() / "data" / "audio" / audio_filename
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
