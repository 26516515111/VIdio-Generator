from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_type = Column(String(20), nullable=False)  # text, image
    input_content = Column(Text, nullable=False)  # 输入内容或图片路径
    scene_description = Column(Text, nullable=True)  # 场景描述
    detected_emotion = Column(String(50), nullable=True)  # 检测到的情绪
    processing_type = Column(String(50), nullable=True)  # 加工类型
    processed_text = Column(Text, nullable=True)  # 处理后的文字
    audio_path = Column(String(200), nullable=True)  # 语音文件路径
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="history")
