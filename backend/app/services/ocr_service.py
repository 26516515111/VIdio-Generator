import httpx
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from ..config import settings
from ..services.user_service import user_service


class OcrService:
    async def extract_text_from_image(
        self,
        image_data: bytes,
        user_id: int,
        db: Session,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        从图片中提取文字和场景信息
        """
        # 获取用户的API密钥
        base_url = None
        if provider:
            api_keys = user_service.get_user_api_keys(
                db, user_id, service_type="ocr"
            )
            api_key = next((k for k in api_keys if k.provider == provider), None)
        else:
            # 先查找默认的，如果没有则查找任意一个
            api_key = user_service.get_default_api_key(db, user_id, "ocr")
            if not api_key:
                api_keys = user_service.get_user_api_keys(db, user_id, service_type="ocr")
                api_key = api_keys[0] if api_keys else None

        if not api_key:
            # 使用默认的小米Token Plan API密钥
            api_key_value = settings.XIAOMI_TOKENPLAN_API_KEY
            provider = "xiaomi-tokenplan"
            base_url = settings.XIAOMI_TOKENPLAN_API_BASE
        else:
            api_key_value = api_key.api_key
            provider = api_key.provider
            base_url = api_key.base_url

        # 根据提供商调用不同的API
        if not api_key_value:
            raise Exception("未找到OCR API密钥，请先在个人中心配置API密钥")
        
        if provider in ["xiaomi", "xiaomi-tokenplan"]:
            return await self._call_xiaomi_ocr(image_data, api_key_value, base_url)
        elif provider == "baidu":
            return await self._call_baidu_ocr(image_data, api_key_value, base_url)
        else:
            raise ValueError(f"Unsupported OCR provider: {provider}")

    async def _call_xiaomi_ocr(self, image_data: bytes, api_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """调用小米MiMo V2.5多模态能力 (OpenAI兼容格式)"""
        if not api_key:
            raise Exception("请先配置小米 Token Plan API 密钥")
        
        url = f"{base_url or settings.XIAOMI_API_BASE}/chat/completions"
        import base64
        image_base64 = base64.b64encode(image_data).decode()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "mimo-v2.5",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "请提取图片中的文字，并描述图片场景。返回格式：{\"text\": \"提取的文字\", \"scene\": \"场景描述\", \"confidence\": 0.95}"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "temperature": 0.3,
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                raise Exception(f"Xiaomi OCR API error: {response.text}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 尝试解析JSON响应
            import json
            try:
                ocr_result = json.loads(content)
                return {
                    "text": ocr_result.get("text", ""),
                    "scene": ocr_result.get("scene", "unknown"),
                    "confidence": ocr_result.get("confidence", 0.9),
                }
            except json.JSONDecodeError:
                # 如果解析失败，直接返回内容
                return {
                    "text": content,
                    "scene": "unknown",
                    "confidence": 0.9,
                }

    async def _call_baidu_ocr(self, image_data: bytes, api_key: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """调用百度OCR API"""
        import base64

        url = f"{base_url or settings.BAIDU_OCR_BASE_URL}/rest/2.0/ocr/v1/general_basic"
        async with httpx.AsyncClient() as client:
            image_base64 = base64.b64encode(image_data).decode()

            response = await client.post(
                url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "image": image_base64,
                    "access_token": api_key,
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                raise Exception(f"Baidu OCR API error: {response.text}")

            result = response.json()
            text = " ".join([item["words"] for item in result.get("words_result", [])])
            return {
                "text": text,
                "scene": "unknown",
                "confidence": 0.9,
            }


ocr_service = OcrService()
