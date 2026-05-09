from typing import List, Optional

from sqlalchemy.orm import Session

from ..models.api_key import ApiKey
from ..models.history import History
from ..models.user import User


class UserService:
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def update_user(db: Session, user: User, email: Optional[str] = None) -> User:
        if email is not None:
            user.email = email
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate_user(db: Session, user: User) -> User:
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    # API Key methods
    @staticmethod
    def add_api_key(
        db: Session,
        user_id: int,
        service_type: str,
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        is_default: bool = False,
    ) -> ApiKey:
        # 如果设置为默认，先取消其他默认
        if is_default:
            db.query(ApiKey).filter(
                ApiKey.user_id == user_id,
                ApiKey.service_type == service_type,
                ApiKey.is_default.is_(True),
            ).update({"is_default": False})
        
        # 如果是该服务类型的第一个API key，自动设为默认
        existing_keys = db.query(ApiKey).filter(
            ApiKey.user_id == user_id,
            ApiKey.service_type == service_type,
        ).count()
        
        if existing_keys == 0:
            is_default = True

        db_api_key = ApiKey(
            user_id=user_id,
            service_type=service_type,
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            is_default=is_default,
        )
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        return db_api_key

    @staticmethod
    def get_user_api_keys(
        db: Session, user_id: int, service_type: Optional[str] = None
    ) -> List[ApiKey]:
        query = db.query(ApiKey).filter(ApiKey.user_id == user_id)
        if service_type:
            query = query.filter(ApiKey.service_type == service_type)
        return query.all()

    @staticmethod
    def get_default_api_key(
        db: Session, user_id: int, service_type: str
    ) -> Optional[ApiKey]:
        return (
            db.query(ApiKey)
            .filter(
                ApiKey.user_id == user_id,
                ApiKey.service_type == service_type,
                ApiKey.is_default.is_(True),
            )
            .first()
        )

    @staticmethod
    def delete_api_key(db: Session, api_key_id: int, user_id: int) -> bool:
        api_key = (
            db.query(ApiKey)
            .filter(ApiKey.id == api_key_id, ApiKey.user_id == user_id)
            .first()
        )
        if api_key:
            db.delete(api_key)
            db.commit()
            return True
        return False

    # History methods
    @staticmethod
    def add_history(db: Session, user_id: int, **kwargs) -> History:
        db_history = History(user_id=user_id, **kwargs)
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    @staticmethod
    def get_user_history(db: Session, user_id: int, limit: int = 10) -> List[History]:
        return (
            db.query(History)
            .filter(History.user_id == user_id)
            .order_by(History.created_at.desc())
            .limit(limit)
            .all()
        )


user_service = UserService()
