import httpx
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from ..config import settings
from ..services.user_service import user_service


class LlmService:
    async def process_text(
        self,
        text: str,
        scene: str,
        emotion: Optional[str] = None,
        processing_type: Optional[str] = None,
        user_id: int = None,
        db: Session = None,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """使用大模型处理文字"""
        # 获取用户的API密钥
        api_key_value = settings.XIAOMI_API_KEY
        resolved_provider = provider or "xiaomi"

        if db and user_id:
            if provider:
                api_keys = user_service.get_user_api_keys(
                    db, user_id, service_type="llm"
                )
                api_key = next(
                    (k for k in api_keys if k.provider == provider), None
                )
            else:
                api_key = user_service.get_default_api_key(
                    db, user_id, "llm"
                )

            if api_key:
                api_key_value = api_key.api_key
                resolved_provider = api_key.provider

        # 构建提示词
        prompt = self._build_prompt(text, scene, emotion, processing_type)

        # 根据提供商调用不同的API
        if resolved_provider == "xiaomi":
            return await self._call_xiaomi_llm(prompt, api_key_value)
        elif resolved_provider == "openai":
            return await self._call_openai_llm(prompt, api_key_value)
        else:
            raise ValueError(f"Unsupported LLM provider: {resolved_provider}")

    def _build_prompt(
        self,
        text: str,
        scene: str,
        emotion: Optional[str] = None,
        processing_type: Optional[str] = None,
    ) -> str:
        """构建提示词"""
        prompt = f"请根据以下信息处理文字：\n\n原始文字：{text}\n场景：{scene}"

        if emotion:
            prompt += f"\n情绪：{emotion}"

        if processing_type:
            prompt += f"\n加工类型：{processing_type}"

        prompt += "\n\n请根据场景和情绪，对文字进行适当加工，使其更符合场景氛围。"

        return prompt

    async def _call_xiaomi_llm(
        self, prompt: str, api_key: str
    ) -> Dict[str, Any]:
        """调用小米MiMo V2.5 Pro"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.XIAOMI_API_BASE}/llm/chat",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "mimo-v2.5-pro",
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的文字加工助手，擅长根据场景和情绪调整文字表达。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                },
                timeout=60.0,
            )

            if response.status_code != 200:
                raise Exception(f"Xiaomi LLM API error: {response.text}")

            result = response.json()
            return {
                "processed_text": result["choices"][0]["message"]["content"],
                "detected_emotion": "neutral",
                "processing_type": "general",
            }

    async def _call_openai_llm(
        self, prompt: str, api_key: str
    ) -> Dict[str, Any]:
        """调用OpenAI API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的文字加工助手，擅长根据场景和情绪调整文字表达。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                },
                timeout=60.0,
            )

            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")

            result = response.json()
            return {
                "processed_text": result["choices"][0]["message"]["content"],
                "detected_emotion": "neutral",
                "processing_type": "general",
            }


llm_service = LlmService()
