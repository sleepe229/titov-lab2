import pytest

from app.schemas import UserCreate, UserUpdate
from app.storage import EmailAlreadyExistsError, UserNotFoundError, UserStorage


@pytest.fixture
def storage():
    return UserStorage()


def test_ids_are_sequential(storage):
    a = storage.create(UserCreate(name="A", email="a@example.com"))
    b = storage.create(UserCreate(name="B", email="b@example.com"))
    assert (a.id, b.id) == (1, 2)


def test_email_is_case_insensitive_unique(storage):
    storage.create(UserCreate(name="A", email="a@example.com"))
    with pytest.raises(EmailAlreadyExistsError):
        storage.create(UserCreate(name="A2", email="A@EXAMPLE.COM"))


def test_update_keeps_own_email(storage):
    a = storage.create(UserCreate(name="A", email="a@example.com"))
    updated = storage.update(a.id, UserUpdate(email="a@example.com", name="A1"))
    assert updated.name == "A1"


def test_get_missing_raises(storage):
    with pytest.raises(UserNotFoundError):
        storage.get(1)


def test_clear_resets_ids(storage):
    storage.create(UserCreate(name="A", email="a@example.com"))
    storage.clear()
    assert storage.list() == []
    assert storage.create(UserCreate(name="B", email="b@example.com")).id == 1
