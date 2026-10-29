"""REST API для управления пользователями."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, Response, status

from app import __version__
from app.schemas import User, UserCreate, UserUpdate
from app.storage import EmailAlreadyExistsError, UserNotFoundError, UserStorage

app = FastAPI(title="User Management API", version=__version__)
storage = UserStorage()


def _not_found(user_id: int) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"User {user_id} not found")


def _conflict(email: str) -> HTTPException:
    return HTTPException(status.HTTP_409_CONFLICT, f"Email {email} already exists")


@app.get("/health")
def health() -> dict[str, str]:
    """Проверка работоспособности сервиса."""
    return {"status": "ok", "version": __version__}


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate) -> User:
    """Создать нового пользователя."""
    try:
        return storage.create(data)
    except EmailAlreadyExistsError:
        raise _conflict(data.email) from None


@app.get("/users", response_model=list[User])
def list_users(
    search: str | None = Query(default=None, description="Поиск по имени или email"),
    limit: int | None = Query(default=None, ge=1, le=100, description="Размер страницы"),
    offset: int = Query(default=0, ge=0, description="Смещение от начала списка"),
) -> list[User]:
    """Получить список пользователей с поиском и пагинацией."""
    return storage.list(search=search, limit=limit, offset=offset)


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    """Получить пользователя по идентификатору."""
    try:
        return storage.get(user_id)
    except UserNotFoundError:
        raise _not_found(user_id) from None


@app.patch("/users/{user_id}", response_model=User)
def update_user(user_id: int, data: UserUpdate) -> User:
    """Частично обновить данные пользователя."""
    try:
        return storage.update(user_id, data)
    except UserNotFoundError:
        raise _not_found(user_id) from None
    except EmailAlreadyExistsError:
        raise _conflict(str(data.email)) from None


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> Response:
    """Удалить пользователя."""
    try:
        storage.delete(user_id)
    except UserNotFoundError:
        raise _not_found(user_id) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
