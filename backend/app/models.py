from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .extensions import db
from werkzeug.security import check_password_hash, generate_password_hash


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True)
    password_hash = Column(String(255), nullable=False)

    paintings = relationship("Painting", back_populates="user", cascade="all,delete")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Painting(db.Model, TimestampMixin):
    __tablename__ = "paintings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255))
    filename = Column(String(512), nullable=False)
    thumbnail = Column(String(512))
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String(16))
    tools_used = Column(Text)
    tags = Column(Text)
    folder = Column(String(255))

    user = relationship("User", back_populates="paintings")

    def serialize_tags(self) -> list[str]:
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

