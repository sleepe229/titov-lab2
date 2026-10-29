"""Pydantic-схемы пользователя."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Общие поля пользователя."""

    name: str = Field(min_length=1, max_length=100, description="Имя пользователя")
    email: EmailStr = Field(description="Уникальный адрес электронной почты")
    age: int | None = Field(default=None, ge=0, le=150, description="Возраст")


class UserCreate(UserBase):
    """Данные для создания пользователя."""


class UserUpdate(BaseModel):
    """Данные для частичного обновления пользователя."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    age: int | None = Field(default=None, ge=0, le=150)


class User(UserBase):
    """Пользователь, сохранённый в системе."""

    id: int = Field(description="Идентификатор пользователя")
    created_at: datetime = Field(description="Дата и время создания (UTC)")
