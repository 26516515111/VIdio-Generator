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
        if provider:
            api_keys = user_service.get_user_api_keys(
                db, user_id, service_type="ocr"
            )
            api_key = next((k for k in api_keys if k.provider == provider), None)
        else:
            api_key = user_service.get_default_api_key(db, user_id, "ocr")

        if not api_key:
            # 使用默认的小米API密钥
            api_key_value = settings.XIAOMI_API_KEY
            provider = "xiaomi"
        else:
            api_key_value = api_key.api_key
            provider = api_key.provider

        # 根据提供商调用不同的API
        if provider == "xiaomi":
            return await self._call_xiaomi_ocr(image_data, api_key_value)
        elif provider == "baidu":
            return await self._call_baidu_ocr(image_data, api_key_value)
        else:
            raise ValueError(f"Unsupported OCR provider: {provider}")

    async def _call_xiaomi_ocr(self, image_data: bytes, api_key: str) -> Dict[str, Any]:
        """调用小米MiMo V2.5多模态能力"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.XIAOMI_API_BASE}/ocr",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"image": ("image.jpg", image_data, "image/jpeg")},
                timeout=30.0,
            )

            if response.status_code != 200:
                raise Exception(f"Xiaomi OCR API error: {response.text}")

            result = response.json()
            return {
                "text": result.get("text", ""),
                "scene": result.get("scene", "unknown"),
                "confidence": result.get("confidence", 0.0),
            }

    async def _call_baidu_ocr(self, image_data: bytes, api_key: str) -> Dict[str, Any]:
        """调用百度OCR API"""
        import base64

        async with httpx.AsyncClient() as client:
            image_base64 = base64.b64encode(image_data).decode()

            response = await client.post(
                "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic",
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
