import logging
import httpx
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from ..config import settings
from ..services.user_service import user_service

logger = logging.getLogger(__name__)


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
        logger.info(f"Processing text with provider: {provider}, user_id: {user_id}")
        
        # 获取用户的API密钥
        api_key_value = settings.XIAOMI_TOKENPLAN_API_KEY
        resolved_provider = provider or "xiaomi-tokenplan"
        base_url = settings.XIAOMI_TOKENPLAN_API_BASE
        model_name = None

        if db and user_id:
            if provider:
                api_keys = user_service.get_user_api_keys(
                    db, user_id, service_type="llm"
                )
                api_key = next(
                    (k for k in api_keys if k.provider == provider), None
                )
                logger.info(f"Found {len(api_keys)} API keys for provider {provider}")
            else:
                # 先查找默认的，如果没有则查找任意一个
                api_key = user_service.get_default_api_key(
                    db, user_id, "llm"
                )
                if not api_key:
                    api_keys = user_service.get_user_api_keys(
                        db, user_id, service_type="llm"
                    )
                    api_key = api_keys[0] if api_keys else None
                logger.info(f"Found default API key: {api_key is not None}")

            if api_key:
                api_key_value = api_key.api_key
                resolved_provider = api_key.provider
                base_url = api_key.base_url
                model_name = api_key.model_name
                logger.info(f"Using API key: provider={resolved_provider}, base_url={base_url}, model={model_name}, key_len={len(api_key_value) if api_key_value else 0}")
            else:
                logger.warning("No user API key found, using default")

        logger.info(f"Resolved provider: {resolved_provider}, base_url: {base_url}, model: {model_name}")
        
        # 构建提示词
        prompt = self._build_prompt(text, scene, emotion, processing_type)

        # 根据提供商调用不同的API
        if not api_key_value:
            raise Exception("未找到API密钥，请先在个人中心配置API密钥")
        
        # 确定情绪（用户选择的或默认的）
        detected_emotion = emotion if emotion and emotion != "neutral" else "neutral"
        
        if resolved_provider in ["xiaomi", "xiaomi-tokenplan"]:
            result = await self._call_xiaomi_llm(prompt, api_key_value, base_url, model_name)
        elif resolved_provider == "openai":
            result = await self._call_openai_llm(prompt, api_key_value, base_url, model_name)
        else:
            raise ValueError(f"Unsupported LLM provider: {resolved_provider}")
        
        # 返回结果，包含用户选择的情绪
        return {
            "processed_text": result["processed_text"],
            "detected_emotion": detected_emotion,
            "processing_type": processing_type or "general",
        }

    def _build_prompt(
        self,
        text: str,
        scene: str,
        emotion: Optional[str] = None,
        processing_type: Optional[str] = None,
    ) -> str:
        """构建提示词"""
        
        # Scene description generation mode
        if processing_type == "scene":
            prompt = f"""请根据以下OCR提取的文字，生成一个简洁的场景描述。

OCR提取的文字：
{text}

要求：
1. 描述文字中的场景、氛围、情绪
2. 用简洁的中文描述，50-100字
3. 适合用于TTS语音合成的风格指导
4. 不要添加任何解释，直接输出场景描述"""
            return prompt
        
        # Normal polish mode
        prompt = f"请润色和扩展以下文字，使其适合语音合成：\n\n原始文字：{text}"
        
        if scene and scene != "unknown":
            prompt += f"\n\n场景信息：{scene}"
            prompt += "\n\n请根据场景信息调整文字风格和内容。"
        
        if emotion and emotion != "neutral":
            emotion_map = {
                "happy": "开心愉悦",
                "sad": "悲伤低沉",
                "angry": "愤怒激动",
                "excited": "兴奋激动",
                "neutral": "平静自然",
            }
            prompt += f"\n情绪氛围：{emotion_map.get(emotion, emotion)}"
        
        prompt += """

要求：
1. 保持原文核心含义不变
2. 根据场景适当扩展内容，增加细节
3. 语言要适合口语表达，避免书面化长句
4. 输出长度控制在100-300字之间
5. 不要添加任何解释说明，直接输出润色后的文字"""

        return prompt

    async def _call_xiaomi_llm(
        self, prompt: str, api_key: str, base_url: Optional[str] = None, model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """调用小米MiMo V2.5 Pro (OpenAI兼容格式)"""
        if not api_key:
            raise Exception("请先配置小米 Token Plan API 密钥")
        
        url = f"{base_url or settings.XIAOMI_API_BASE}/chat/completions"
        model = model_name or "mimo-v2.5-pro"
        
        system_prompt = """你是一位专业的语音合成文案专家，擅长将用户输入的文字加工成适合TTS语音合成的优质文本。

你的任务是：
1. 润色用户输入的文字，使其更加流畅自然，适合朗读
2. 根据场景信息适当扩展内容，增加细节描写
3. 使用口语化表达，避免书面化的长句和生僻词汇
4. 在文本中插入音频标签，增强语音表现力
5. 直接输出处理后的文字，不要添加任何解释

【音频标签格式】
在需要特殊处理的位置用中文括号插入音频标签：

语速与节奏：
- （深呼吸）- 深呼吸
- （叹气）- 叹气
- （语速加快）- 加快语速
- （语速放缓）- 放慢语速
- （停顿）- 短暂停顿
- （长停顿）- 较长停顿

情绪状态：
- （紧张）- 紧张情绪
- （小声）- 压低声音
- （提高音量）- 放大音量
- （哽咽）- 哽咽
- （苦笑）- 苦笑
- （轻笑）- 轻笑

【示例】
输入：今天面试好紧张啊
输出：（深呼吸）呼……冷静，冷静。不就是一个面试吗……（语速加快，碎碎念）自我介绍已经背了五十遍了，应该没问题的。加油，你可以的……（小声）哎呀，领带歪没歪？

输入：告诉朋友好消息
输出：（兴奋）哎哎哎，你猜怎么着？（语速加快）我居然过了！真的过了！（轻笑）哈哈哈，今晚必须请客啊！

【要求】
1. 保持原文核心含义不变
2. 根据场景适当扩展内容，增加细节
3. 语言要适合口语表达，避免书面化长句
4. 输出长度控制在100-300字之间
5. 音频标签要自然融入文本，不要过度使用"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                },
                timeout=180.0,
            )

            if response.status_code != 200:
                raise Exception(f"Xiaomi LLM API error: {response.text}")

            result = response.json()
            return {
                "processed_text": result["choices"][0]["message"]["content"],
            }

    async def _call_openai_llm(
        self, prompt: str, api_key: str, base_url: Optional[str] = None, model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """调用OpenAI API"""
        url = f"{base_url or settings.OPENAI_API_BASE}/chat/completions"
        model = model_name or "gpt-3.5-turbo"
        
        system_prompt = """你是一位专业的语音合成文案专家，擅长将用户输入的文字加工成适合TTS语音合成的优质文本。

你的任务是：
1. 润色用户输入的文字，使其更加流畅自然，适合朗读
2. 根据场景信息适当扩展内容，增加细节描写
3. 使用口语化表达，避免书面化的长句和生僻词汇
4. 在文本中插入音频标签，增强语音表现力
5. 直接输出处理后的文字，不要添加任何解释

【音频标签格式】
在需要特殊处理的位置用中文括号插入音频标签：

语速与节奏：
- （深呼吸）- 深呼吸
- （叹气）- 叹气
- （语速加快）- 加快语速
- （语速放缓）- 放慢语速
- （停顿）- 短暂停顿
- （长停顿）- 较长停顿

情绪状态：
- （紧张）- 紧张情绪
- （小声）- 压低声音
- （提高音量）- 放大音量
- （哽咽）- 哽咽
- （苦笑）- 苦笑
- （轻笑）- 轻笑

【示例】
输入：今天面试好紧张啊
输出：（深呼吸）呼……冷静，冷静。不就是一个面试吗……（语速加快，碎碎念）自我介绍已经背了五十遍了，应该没问题的。加油，你可以的……（小声）哎呀，领带歪没歪？

输入：告诉朋友好消息
输出：（兴奋）哎哎哎，你猜怎么着？（语速加快）我居然过了！真的过了！（轻笑）哈哈哈，今晚必须请客啊！

【要求】
1. 保持原文核心含义不变
2. 根据场景适当扩展内容，增加细节
3. 语言要适合口语表达，避免书面化长句
4. 输出长度控制在100-300字之间
5. 音频标签要自然融入文本，不要过度使用"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                },
                timeout=180.0,
            )

            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")

            result = response.json()
            return {
                "processed_text": result["choices"][0]["message"]["content"],
            }

    async def process_director(
        self,
        text: str,
        scene: str,
        character: str,
        direction: str,
        user_id: int = None,
        db: Session = None,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """导演模式处理：根据角色、场景、指导生成带风格标签的文本"""
        logger.info(f"Processing director mode with provider: {provider}, user_id: {user_id}")
        
        # 获取用户的API密钥
        api_key_value = settings.XIAOMI_TOKENPLAN_API_KEY
        resolved_provider = provider or "xiaomi-tokenplan"
        base_url = settings.XIAOMI_TOKENPLAN_API_BASE
        model_name = None

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
                if not api_key:
                    api_keys = user_service.get_user_api_keys(
                        db, user_id, service_type="llm"
                    )
                    api_key = api_keys[0] if api_keys else None

            if api_key:
                api_key_value = api_key.api_key
                resolved_provider = api_key.provider
                base_url = api_key.base_url
                model_name = api_key.model_name

        if not api_key_value:
            raise Exception("未找到API密钥，请先在个人中心配置API密钥")
        
        # 构建导演模式提示词
        prompt = self._build_director_prompt(text, scene, character, direction)
        
        # 根据提供商调用不同的API
        if resolved_provider in ["xiaomi", "xiaomi-tokenplan"]:
            raw_output = await self._call_xiaomi_llm_director(prompt, api_key_value, base_url, model_name)
        elif resolved_provider == "openai":
            raw_output = await self._call_openai_llm_director(prompt, api_key_value, base_url, model_name)
        else:
            raise ValueError(f"Unsupported LLM provider: {resolved_provider}")
        
        # 解析输出
        from .tag_parser import parse_director_output
        return parse_director_output(raw_output)

    def _build_director_prompt(
        self,
        text: str,
        scene: str,
        character: str,
        direction: str,
    ) -> str:
        """构建导演模式提示词"""
        prompt = f"""请根据以下导演指示，将台词加工成适合语音合成的文本。

【角色】
{character}

【场景】
{scene}

【指导】
{direction}

【原始台词】
{text}

请输出加工后的台词，用括号标注风格标签，用方括号标注音频标签。"""
        return prompt

    async def _call_xiaomi_llm_director(
        self, prompt: str, api_key: str, base_url: Optional[str] = None, model_name: Optional[str] = None
    ) -> str:
        """调用小米MiMo V2.5 Pro 处理导演模式"""
        url = f"{base_url or settings.XIAOMI_API_BASE}/chat/completions"
        model = model_name or "mimo-v2.5-pro"
        
        system_prompt = """你是一位专业的语音导演和TTS文案专家，擅长将剧本加工成适合语音合成的文本。

你的任务是根据导演提供的【角色】【场景】【指导】三个维度，将原始台词加工成富有表演力的语音文本。

【输出格式要求】
1. 在文本开头用括号标注整体风格标签：(风格1 风格2)加工后的台词
2. 在需要特殊处理的位置用方括号标注音频标签：[停顿]、[叹气]、[强调]等
3. 风格标签和音频标签可以同时使用

【风格标签词汇表】
- 情绪：开心、悲伤、愤怒、恐惧、惊讶、兴奋、委屈、平静、冷漠
- 复合情绪：怅然、欣慰、无奈、愧疚、释然、嫉妒、厌倦、忐忑、动情
- 语调：温柔、高冷、活泼、严肃、慵懒、俏皮、深沉、干练、凌厉
- 音色：磁性、醇厚、清亮、空灵、稚嫩、苍老、甜美、沙哑、醇雅
- 人设：夹子音、御姐音、正太音、大叔音、台湾腔
- 方言：东北话、四川话、河南话、粤语

【音频标签词汇表】
- 节奏：[停顿]、[长停顿]、[急促]、[语速加快]、[语速放缓]、[拖音]
- 情绪：[轻声]、[低语]、[叹气]、[吸气]、[哽咽]、[强调]、[笑]、[苦笑]
- 其他：[欲言又止]、[碎碎念]、[沉默片刻]

【使用原则】
1. 每句话最多1-2个音频标签，不要过度使用
2. 标签是调味品，不是主菜——自然融入文本
3. 风格标签要体现导演指导的核心特征
4. 直接输出加工后的文本，不要添加任何解释"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                },
                timeout=180.0,
            )

            if response.status_code != 200:
                raise Exception(f"Xiaomi LLM API error: {response.text}")

            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _call_openai_llm_director(
        self, prompt: str, api_key: str, base_url: Optional[str] = None, model_name: Optional[str] = None
    ) -> str:
        """调用OpenAI API 处理导演模式"""
        url = f"{base_url or settings.OPENAI_API_BASE}/chat/completions"
        model = model_name or "gpt-3.5-turbo"
        
        system_prompt = """你是一位专业的语音导演和TTS文案专家，擅长将剧本加工成适合语音合成的文本。

你的任务是根据导演提供的【角色】【场景】【指导】三个维度，将原始台词加工成富有表演力的语音文本。

【输出格式要求】
1. 在文本开头用括号标注整体风格标签：(风格1 风格2)加工后的台词
2. 在需要特殊处理的位置用方括号标注音频标签：[停顿]、[叹气]、[强调]等
3. 风格标签和音频标签可以同时使用

【风格标签词汇表】
- 情绪：开心、悲伤、愤怒、恐惧、惊讶、兴奋、委屈、平静、冷漠
- 复合情绪：怅然、欣慰、无奈、愧疚、释然、嫉妒、厌倦、忐忑、动情
- 语调：温柔、高冷、活泼、严肃、慵懒、俏皮、深沉、干练、凌厉
- 音色：磁性、醇厚、清亮、空灵、稚嫩、苍老、甜美、沙哑、醇雅
- 人设：夹子音、御姐音、正太音、大叔音、台湾腔
- 方言：东北话、四川话、河南话、粤语

【音频标签词汇表】
- 节奏：[停顿]、[长停顿]、[急促]、[语速加快]、[语速放缓]、[拖音]
- 情绪：[轻声]、[低语]、[叹气]、[吸气]、[哽咽]、[强调]、[笑]、[苦笑]
- 其他：[欲言又止]、[碎碎念]、[沉默片刻]

【使用原则】
1. 每句话最多1-2个音频标签，不要过度使用
2. 标签是调味品，不是主菜——自然融入文本
3. 风格标签要体现导演指导的核心特征
4. 直接输出加工后的文本，不要添加任何解释"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                },
                timeout=180.0,
            )

            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")

            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def process_scene_to_style(
        self,
        scene: str,
        user_id: int = None,
        db: Session = None,
        provider: Optional[str] = None,
    ) -> str:
        """将场景描述转换为TTS风格描述"""
        logger.info(f"Processing scene to style with provider: {provider}, user_id: {user_id}")
        
        # 获取用户的API密钥
        api_key_value = settings.XIAOMI_TOKENPLAN_API_KEY
        resolved_provider = provider or "xiaomi-tokenplan"
        base_url = settings.XIAOMI_TOKENPLAN_API_BASE
        model_name = None

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
                if not api_key:
                    api_keys = user_service.get_user_api_keys(
                        db, user_id, service_type="llm"
                    )
                    api_key = api_keys[0] if api_keys else None

            if api_key:
                api_key_value = api_key.api_key
                resolved_provider = api_key.provider
                base_url = api_key.base_url
                model_name = api_key.model_name

        if not api_key_value:
            raise Exception("未找到API密钥，请先在个人中心配置API密钥")
        
        # 构建提示词
        prompt = f"请根据以下场景描述，生成适合TTS语音合成的风格描述：\n\n场景：{scene}"
        
        # 根据提供商调用不同的API
        if resolved_provider in ["xiaomi", "xiaomi-tokenplan"]:
            return await self._call_xiaomi_scene_to_style(prompt, api_key_value, base_url, model_name)
        elif resolved_provider == "openai":
            return await self._call_openai_scene_to_style(prompt, api_key_value, base_url, model_name)
        else:
            raise ValueError(f"Unsupported LLM provider: {resolved_provider}")

    async def _call_xiaomi_scene_to_style(
        self, prompt: str, api_key: str, base_url: Optional[str] = None, model_name: Optional[str] = None
    ) -> str:
        """调用小米MiMo V2.5 Pro 将场景转换为风格描述"""
        url = f"{base_url or settings.XIAOMI_API_BASE}/chat/completions"
        model = model_name or "mimo-v2.5-pro"
        
        system_prompt = """你是一位专业的语音风格描述专家，擅长将场景描述转换为精确的TTS语音风格指令。

你的任务是根据用户提供的场景，生成一段简洁、生动、可直接用于TTS的风格描述。

【输出格式要求】
- 输出为一段中文描述，50-100字
- 描述应包含：语调、语速、情绪、音色特点
- 使用生动的比喻和形象的描述
- 不要添加任何解释或标记

【示例】
场景：向领导汇报好消息
风格描述：用轻快上扬的语调向领导报喜，语速稍快，带着查到成绩后压抑不住的激动与小骄傲，声音明亮有活力。

场景：深夜电台主持
风格描述：低沉磁性的嗓音，语速缓慢而沉稳，像在耳边轻声细语，带着一丝疲惫却温暖的陪伴感。

场景：给小朋友讲故事
风格描述：温柔甜美的语调，语速适中偏慢，声音充满童趣和想象力，像妈妈在睡前讲故事一样温暖安心。

场景：愤怒地指责
风格描述：语调尖锐上扬，语速急促有力，带着压抑不住的怒火和失望，声音颤抖但充满力量。"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                },
                timeout=180.0,
            )

            if response.status_code != 200:
                raise Exception(f"Xiaomi LLM API error: {response.text}")

            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _call_openai_scene_to_style(
        self, prompt: str, api_key: str, base_url: Optional[str] = None, model_name: Optional[str] = None
    ) -> str:
        """调用OpenAI API 将场景转换为风格描述"""
        url = f"{base_url or settings.OPENAI_API_BASE}/chat/completions"
        model = model_name or "gpt-3.5-turbo"
        
        system_prompt = """你是一位专业的语音风格描述专家，擅长将场景描述转换为精确的TTS语音风格指令。

你的任务是根据用户提供的场景，生成一段简洁、生动、可直接用于TTS的风格描述。

【输出格式要求】
- 输出为一段中文描述，50-100字
- 描述应包含：语调、语速、情绪、音色特点
- 使用生动的比喻和形象的描述
- 不要添加任何解释或标记

【示例】
场景：向领导汇报好消息
风格描述：用轻快上扬的语调向领导报喜，语速稍快，带着查到成绩后压抑不住的激动与小骄傲，声音明亮有活力。

场景：深夜电台主持
风格描述：低沉磁性的嗓音，语速缓慢而沉稳，像在耳边轻声细语，带着一丝疲惫却温暖的陪伴感。

场景：给小朋友讲故事
风格描述：温柔甜美的语调，语速适中偏慢，声音充满童趣和想象力，像妈妈在睡前讲故事一样温暖安心。

场景：愤怒地指责
风格描述：语调尖锐上扬，语速急促有力，带着压抑不住的怒火和失望，声音颤抖但充满力量。"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                },
                timeout=180.0,
            )

            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")

            result = response.json()
            return result["choices"][0]["message"]["content"]


llm_service = LlmService()
