from sqlalchemy import String, Date, Enum, Boolean
from sqlalchemy import DateTime, Integer, func, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.models.base_model import BaseModel
from app.config.pack_roles import Role
from datetime import date


class Users(BaseModel):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now())
    role: Mapped[Enum] = mapped_column(
        "role", Enum(Role), default=Role.USER, nullable=True)
    confirmed: Mapped["bool"] = mapped_column(Boolean, default=False, nullable=True)