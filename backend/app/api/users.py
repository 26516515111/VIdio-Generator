from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..api.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..services.user_service import user_service

router = APIRouter(prefix="/api/users", tags=["users"])


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    service_type: Literal["ocr", "llm", "tts"]
    provider: Literal["xiaomi", "xiaomi-tokenplan", "openai", "baidu", "tencent"]
    api_key: str
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    is_default: bool = False


class ApiKeyResponse(BaseModel):
    id: int
    service_type: str
    provider: str
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    is_default: bool

    class Config:
        from_attributes = True


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    return user_service.update_user(db, current_user, email=update_data.get("email"))


@router.get("/api-keys", response_model=List[ApiKeyResponse])
def get_api_keys(
    service_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_service.get_user_api_keys(db, current_user.id, service_type)


@router.post("/api-keys", response_model=ApiKeyResponse)
def create_api_key(
    api_key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_service.add_api_key(
        db,
        current_user.id,
        api_key_data.service_type,
        api_key_data.provider,
        api_key_data.api_key,
        api_key_data.base_url,
        api_key_data.model_name,
        api_key_data.is_default,
    )


@router.delete("/api-keys/{api_key_id}")
def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = user_service.delete_api_key(db, api_key_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"message": "API key deleted successfully"}


class ModelInfo(BaseModel):
    id: int
    provider: str
    model_name: Optional[str] = None
    is_default: bool


class ModelsByType(BaseModel):
    ocr: List[ModelInfo]
    llm: List[ModelInfo]
    tts: List[ModelInfo]


@router.get("/models", response_model=ModelsByType)
def get_available_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户可用的模型，按服务类型分组"""
    ocr_keys = user_service.get_user_api_keys(db, current_user.id, service_type="ocr")
    llm_keys = user_service.get_user_api_keys(db, current_user.id, service_type="llm")
    tts_keys = user_service.get_user_api_keys(db, current_user.id, service_type="tts")

    def to_model_info(keys):
        return [
            ModelInfo(
                id=k.id,
                provider=k.provider,
                model_name=k.model_name,
                is_default=k.is_default,
            )
            for k in keys
        ]

    return ModelsByType(
        ocr=to_model_info(ocr_keys),
        llm=to_model_info(llm_keys),
        tts=to_model_info(tts_keys),
    )
