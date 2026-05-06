from typing import Optional

from sqlalchemy.orm import Session

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


user_service = UserService()
