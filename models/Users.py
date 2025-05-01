import uuid
from sqlalchemy import Column, String, ARRAY, UUID
from dataclasses import dataclass


from db.base import Base

# Модель User
@dataclass
class Users(Base):
    __tablename__: str = "users"
    id: str = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    email: str = Column(String, unique=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    username: str = Column(String, unique=True, nullable=False)
    birthday: str = Column(String, nullable=True)
    rooms_list: list = Column(ARRAY(String))
    yandex_token: str = Column(String)