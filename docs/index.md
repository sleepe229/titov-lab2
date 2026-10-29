# User Management API

REST API для управления пользователями: создание, получение, обновление и удаление.
Реализовано на **FastAPI**, хранение — в памяти процесса.

## Запуск

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Интерактивная документация OpenAPI доступна по адресу `http://127.0.0.1:8000/docs`.

## Эндпоинты

| Метод  | Путь              | Описание                         |
|--------|-------------------|----------------------------------|
| GET    | `/health`         | Проверка работоспособности       |
| POST   | `/users`          | Создать пользователя             |
| GET    | `/users`          | Список (`search`, `limit`, `offset`) |
| GET    | `/users/{id}`     | Получить пользователя            |
| PATCH  | `/users/{id}`     | Частично обновить пользователя   |
| DELETE | `/users/{id}`     | Удалить пользователя             |

## Тестирование

```bash
pip install -r requirements-dev.txt
flake8 .
pytest -v
```

## CI/CD

- `main.yml` — линтер и тесты на каждый push в любую ветку и на каждый PR в `main`;
- `pr-automerge.yml` — тесты PR в `main` и автоматическое слияние при успехе;
- `docs.yml` — сборка этой документации и публикация в ветку `gh-pages`.
