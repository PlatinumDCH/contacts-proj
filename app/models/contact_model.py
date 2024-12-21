from sqlalchemy import String, Date
from sqlalchemy import DateTime, Integer, func, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.models.base_model import BaseModel
from app.models.users_model import Users
from datetime import date


class Contacts(BaseModel):
    __tablename__ = "contact"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(25))
    phone_number: Mapped[str] = mapped_column(String)
    date_birthday: Mapped[Date] = mapped_column(Date)
    note: Mapped[str] = mapped_column(String, default=None)
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    users_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["Users"] = relationship("Users", backref="todos", lazy="joined")