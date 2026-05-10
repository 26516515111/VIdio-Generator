import sys
from pydantic_settings import BaseSettings
from pathlib import Path

def _get_app_dir() -> Path:
    """获取应用目录：打包后为exe所在目录，开发时为backend目录"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = f"sqlite:///{_get_app_dir() / 'data' / 'app.db'}"
    
    # JWT配置
    SECRET_KEY: str = "dev-secret-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 小米API配置
    XIAOMI_API_KEY: str = ""
    XIAOMI_API_BASE: str = "https://api.xiaomi.com/v1"
    
    # 小米Token Plan配置
    XIAOMI_TOKENPLAN_API_KEY: str = ""
    XIAOMI_TOKENPLAN_API_BASE: str = "https://token-plan-cn.xiaomimimo.com/v1"
    
    # OpenAI配置
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    
    # 百度OCR配置
    BAIDU_OCR_KEY: str = ""
    BAIDU_OCR_SECRET_KEY: str = ""
    BAIDU_OCR_BASE_URL: str = "https://aip.baidubce.com"
    
    # 腾讯TTS配置
    TENCENT_SECRET_ID: str = ""
    TENCENT_SECRET_KEY: str = ""
    TENCENT_TTS_BASE_URL: str = "https://tts.tencentcloudapi.com"
    
    class Config:
        env_file = ".env"

settings = Settings()
