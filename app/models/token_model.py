from sqlalchemy import String
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.models.base_model import BaseModel
from app.models.users_model import Users




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
