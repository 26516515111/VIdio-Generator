from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = f"sqlite:///{Path(__file__).parent.parent / 'data' / 'app.db'}"
    
    # JWT配置
    SECRET_KEY: str  # No default — will raise ValidationError if missing from .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 小米API配置（默认）
    XIAOMI_API_KEY: str = ""
    XIAOMI_API_BASE: str = "https://api.xiaomi.com/v1"
    
    # 其他服务配置（可选）
    OPENAI_API_KEY: str = ""
    BAIDU_OCR_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
