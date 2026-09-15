# File Vault

> Микросервис для безопасной одноразовой передачи файлов и текстовых секретов.

File Vault позволяет создать временную ссылку на файл или текст. Данные шифруются, ссылка имеет ограниченный срок жизни и количество скачиваний, после чего секрет автоматически удаляется.

```text
Upload / Secret
      │
      ▼
  Encryption
      │
      ▼
   Storage
      │
      ▼
 Temporary UUID Link
      │
      ▼
   Download
      │
      ▼
   Destroy
```

Сервис не предназначен для защиты от самого получателя: после раскрытия секрета пользователь может сохранить его самостоятельно. Задача File Vault — не оставлять секрет в постоянном хранилище и сделать его повторное получение через сервис невозможным после использования или истечения TTL.

## Stack

| Category        | Technology                       |
| --------------- | -------------------------------- |
| Language        | Python 3.13+                     |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Backend         | FastAPI                          |
| Validation      | Pydantic                         |
| Database        | PostgreSQL                       |
| ORM             | SQLAlchemy 2                     |
| Migrations      | Alembic                          |
| File storage    | MinIO                            |
| Encryption      | cryptography                     |
| Templates       | Jinja2                           |
| Frontend        | HTML / CSS / JavaScript          |
| Testing         | pytest                           |
| Infrastructure  | Docker / Docker Compose          |

React и другие frontend-фреймворки не используются.

## Architecture

```text
                    ┌─────────────┐
                    │   Browser   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        PostgreSQL       MinIO       Worker
        metadata       encrypted     TTL cleanup
                         files
```

PostgreSQL хранит метаданные, MinIO — зашифрованные файлы. Worker удаляет истёкшие секреты.

## Features

* одноразовые ссылки;
* передача текста и файлов;
* шифрование данных;
* UUID-идентификаторы;
* TTL;
* ограничение количества скачиваний;
* автоматическое удаление;
* REST API;
* Web-интерфейс;
* Swagger/OpenAPI;
* Docker Compose;
* автоматические тесты.

## Project Structure

```text
file-vault/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── templates/
│   ├── static/
│   └── main.py
│
├── worker/
│   └── cleanup.py
│
├── migrations/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

## Development

### Requirements

* Python 3.13+
* [uv](https://docs.astral.sh/uv/)
* Docker
* Docker Compose

### Install

Clone the repository and install dependencies:

```bash
uv sync
```

`uv` автоматически создаст виртуальное окружение и установит зависимости из `pyproject.toml` и `uv.lock`.

### Environment

```bash
cp .env.example .env
```

Заполни необходимые переменные окружения в `.env`.

### Run

Запуск инфраструктуры:

```bash
docker compose up -d
```

Запуск приложения:

```bash
uv run fastapi dev app/main.py
```

После запуска:

```text
Application    http://localhost:8000
Swagger        http://localhost:8000/docs
```

Для запуска всего окружения через Docker:

```bash
docker compose up --build
```

### Tests

```bash
uv run pytest
```

### Migrations

Создание миграции:

```bash
uv run alembic revision --autogenerate -m "description"
```

Применение миграций:

```bash
uv run alembic upgrade head
```

## API

Основные endpoints:

```text
POST   /api/secrets
GET    /api/secrets/{id}
GET    /api/secrets/{id}/download
DELETE /api/secrets/{id}
GET    /api/health
```

Полная интерактивная документация доступна через Swagger:

```text
http://localhost:8000/docs
```

## Roadmap

### Version 1.0

* [ ] FastAPI application
* [ ] PostgreSQL
* [ ] MinIO
* [ ] File upload
* [ ] Text secrets
* [ ] Encryption
* [ ] UUID links
* [ ] TTL
* [ ] Download limits
* [ ] Automatic cleanup
* [ ] Web interface
* [ ] REST API
* [ ] Tests
* [ ] Docker Compose

### Future

* [ ] User accounts
* [ ] API keys
* [ ] Team workspaces
* [ ] Client-side encryption
* [ ] CLI
* [ ] Billing
* [ ] Production object storage
* [ ] Monitoring and rate limiting

## License

This project is developed as a study project with the possibility of further development into a commercial SaaS.
