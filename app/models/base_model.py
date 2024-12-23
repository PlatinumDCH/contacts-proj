from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Date, Enum, Boolean
from sqlalchemy import DateTime, Integer, func, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.config.pack_roles import Role
from datetime import date

class BaseModel(DeclarativeBase):
    ...

class Contacts(BaseModel):
    __tablename__ = "contacts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(25))
    phone_number: Mapped[str] = mapped_column(String)
    # date_birthday: Mapped[Date] = mapped_column(Date)
    note: Mapped[str] = mapped_column(String, default=None)
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    # users_id: Mapped[int] = mapped_column(
    #     Integer, ForeignKey("users.id"), nullable=True)
    # user: Mapped["Users"] = relationship("Users", backref="todos", lazy="joined")


class UserTokensTable(BaseModel):
    __tablename__ = "user_tokens"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    reset_password_token: Mapped[str] = mapped_column(String(255), nullable=True)
    email_token: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    user: Mapped["Users"] = relationship("Users", backref="tokens", lazy="joined")

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