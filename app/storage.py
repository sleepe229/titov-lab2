"""Хранилище пользователей в памяти."""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from app.schemas import User, UserCreate, UserUpdate


class UserNotFoundError(Exception):
    """Пользователь с указанным идентификатором не найден."""


class EmailAlreadyExistsError(Exception):
    """Пользователь с таким email уже зарегистрирован."""


class UserStorage:
    """Потокобезопасное хранилище пользователей в оперативной памяти.

    Идентификаторы выдаются последовательно, начиная с 1.
    """

    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id = 1
        self._lock = Lock()

    def _ensure_email_free(self, email: str, exclude_id: int | None = None) -> None:
        for user in self._users.values():
            if user.email.lower() == email.lower() and user.id != exclude_id:
                raise EmailAlreadyExistsError(email)

    def create(self, data: UserCreate) -> User:
        """Создать пользователя и вернуть его с присвоенным id."""
        with self._lock:
            self._ensure_email_free(data.email)
            user = User(
                id=self._next_id,
                created_at=datetime.now(timezone.utc),
                **data.model_dump(),
            )
            self._users[user.id] = user
            self._next_id += 1
            return user

    def get(self, user_id: int) -> User:
        """Вернуть пользователя по id или выбросить UserNotFoundError."""
        try:
            return self._users[user_id]
        except KeyError:
            raise UserNotFoundError(user_id) from None

    def list(self) -> list[User]:
        """Вернуть всех пользователей, отсортированных по id."""
        return sorted(self._users.values(), key=lambda u: u.id)

    def update(self, user_id: int, data: UserUpdate) -> User:
        """Частично обновить пользователя (только переданные поля)."""
        with self._lock:
            user = self.get(user_id)
            changes = data.model_dump(exclude_unset=True)
            if "email" in changes:
                self._ensure_email_free(changes["email"], exclude_id=user_id)
            updated = user.model_copy(update=changes)
            self._users[user_id] = updated
            return updated

    def delete(self, user_id: int) -> None:
        """Удалить пользователя по id."""
        with self._lock:
            self.get(user_id)
            del self._users[user_id]

    def clear(self) -> None:
        """Удалить всех пользователей и сбросить счётчик id."""
        with self._lock:
            self._users.clear()
            self._next_id = 1
