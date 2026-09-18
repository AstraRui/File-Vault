# File Vault

> **Передавайте то, что не должно оставаться навсегда.**

File Vault — микросервис для временной и одноразовой передачи файлов и текстовых секретов через защищённые ссылки.

Иногда нужно быстро передать файл, пароль, конфигурацию, токен, ключ или другой чувствительный текст, но отправлять такие данные в обычный мессенджер, почту или оставлять их в облачном хранилище не хочется.

File Vault решает эту задачу через простой принцип:

**создал → передал ссылку → получил → ссылка перестала работать.**

Пользователь загружает файл или вводит текст, задаёт срок жизни ссылки и количество доступных скачиваний. Сервис создаёт уникальную временную ссылку. После достижения лимита скачиваний или окончания TTL секрет становится недоступен и удаляется из хранилища.

При этом File Vault не пытается контролировать самого получателя. После получения данных человек может сохранить их самостоятельно. Задача сервиса другая — **не хранить переданный секрет постоянно и не позволять повторно получить его через File Vault после завершения срока действия или использования.**

---

## Зачем нужен File Vault

Обычная передача чувствительных данных часто выглядит примерно так:

```text
Пароль / файл / токен
        │
        ▼
 Telegram / Email / Cloud
        │
        ▼
 Данные остаются в истории
        │
        ▼
 Их можно получить снова
```

File Vault строится вокруг другого сценария:

```text
        Secret
          │
          ▼
      Encryption
          │
          ▼
 Temporary Storage
          │
          ▼
    One-Time Link
          │
          ▼
       Receiver
          │
          ▼
       Destroy
```

Ссылка существует ограниченное время и может использоваться ограниченное количество раз.

Это делает File Vault удобным инструментом для ситуаций, когда **данные нужно передать, но нет необходимости хранить их после передачи.**

---

## Основные сценарии использования

### Передача файлов

Нужно отправить документ, архив, конфигурационный файл или другой файл без создания постоянной публичной ссылки.

File Vault создаёт временную ссылку, которую можно передать получателю.

### Передача текстовых секретов

Например:

* пароль;
* API token;
* SSH-конфигурация;
* временный ключ;
* конфигурационные параметры;
* другой чувствительный текст.

Получателю не требуется аккаунт — достаточно ссылки.

### Ограниченный доступ

Для секрета можно задать:

* срок действия;
* максимальное количество скачиваний.

После достижения ограничения ссылка перестаёт предоставлять доступ.

---

## Основная идея

File Vault придерживается принципа **minimal persistence** — минимального времени хранения данных.

Секрет не должен превращаться в ещё одну постоянную копию информации.

Жизненный цикл выглядит так:

```text
┌─────────────┐
│   Upload    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Encryption │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Storage   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Temporary   │
│ UUID Link   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Download   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Destroy   │
└─────────────┘
```

---

## Статус проекта

**Early development**

На текущем этапе реализованы:

* базовая структура Python-проекта;
* FastAPI-приложение;
* Jinja2-шаблоны;
* Web-интерфейс;
* первоначальный UI/UX;
* базовая навигация;
* health-check endpoint;
* Swagger/OpenAPI.

Основная серверная логика File Vault находится в разработке.

Следующие этапы — подключение PostgreSQL и MinIO, реализация шифрования, загрузки файлов, временных ссылок, ограничений доступа и автоматического удаления.

---

# Technical Documentation

## Stack

| Category        | Technology              |
| --------------- | ----------------------- |
| Language        | Python 3.13+            |
| Package manager | uv                      |
| Backend         | FastAPI                 |
| Validation      | Pydantic                |
| Configuration   | pydantic-settings       |
| Database        | PostgreSQL              |
| ORM             | SQLAlchemy 2            |
| Migrations      | Alembic                 |
| Object storage  | MinIO                   |
| Encryption      | cryptography            |
| Templates       | Jinja2                  |
| Frontend        | HTML / CSS / JavaScript |
| Testing         | pytest                  |
| HTTP testing    | httpx                   |
| Linting         | Ruff                    |
| Infrastructure  | Docker / Docker Compose |

React и другие frontend-фреймворки не используются.

Frontend реализуется непосредственно через HTML, CSS, JavaScript и серверный рендеринг Jinja2.

---

## Architecture

Планируемая архитектура системы:

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
                 ┌──────────────┼──────────────┐
                 │              │              │
                 ▼              ▼              ▼
          ┌────────────┐ ┌────────────┐ ┌────────────┐
          │ PostgreSQL │ │   MinIO    │ │   Worker   │
          │            │ │            │ │            │
          │ Metadata   │ │ Encrypted  │ │ TTL        │
          │            │ │ Files      │ │ Cleanup    │
          └────────────┘ └────────────┘ └────────────┘
```

### PostgreSQL

Хранит только метаданные секрета:

```text
id
storage_key
file_name
file_size
content_type
created_at
expires_at
download_count
max_downloads
status
```

Содержимое файлов не хранится непосредственно в PostgreSQL.

### MinIO

Используется как объектное хранилище.

В MinIO размещаются зашифрованные объекты файлов.

Архитектура рассчитана на возможность последующей замены MinIO на совместимое с S3 production-хранилище.

### Worker

Отдельный процесс отвечает за очистку истёкших секретов.

Worker периодически проверяет TTL и удаляет:

1. объект из хранилища;
2. соответствующие метаданные из PostgreSQL.

---

## Security Model

Секрет проходит следующий путь:

```text
Input
  │
  ▼
Validation
  │
  ▼
Encryption
  │
  ▼
Storage
  │
  ▼
Temporary UUID
  │
  ▼
Access validation
  │
  ▼
Decrypt
  │
  ▼
Download / Display
  │
  ▼
Destroy
```

При запросе доступа сервис проверяет:

* существование секрета;
* срок действия;
* статус;
* количество предыдущих скачиваний;
* установленный лимит.

Если секрет больше недоступен, сервис не должен предоставлять его содержимое.

> File Vault защищает процесс хранения и повторного доступа через сервис, но не контролирует действия получателя после раскрытия секрета.

---

## Project Structure

```text
file-vault/
│
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── secrets.py
│   │   │   ├── files.py
│   │   │   └── health.py
│   │   │
│   │   └── dependencies.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   │
│   ├── models/
│   │   └── secret.py
│   │
│   ├── schemas/
│   │   └── secret.py
│   │
│   ├── services/
│   │   ├── secret_service.py
│   │   ├── encryption_service.py
│   │   └── storage_service.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── create.html
│   │   ├── secret.html
│   │   └── destroyed.html
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   │
│   └── main.py
│
├── worker/
│   └── cleanup.py
│
├── migrations/
│
├── tests/
│   ├── test_secrets.py
│   ├── test_encryption.py
│   └── test_expiration.py
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── .env.example
├── .gitignore
└── README.md
```

---

## Development

### Requirements

* Python 3.13+
* uv
* Docker
* Docker Compose

### Install

Clone the repository:

```bash
git clone <repository-url>
cd file-vault
```

Install dependencies:

```bash
uv sync
```

`uv` создаст виртуальное окружение и установит зависимости в соответствии с `pyproject.toml` и `uv.lock`.

---

## Environment

Создай локальный файл конфигурации:

```bash
cp .env.example .env
```

После этого заполни необходимые переменные окружения.

Пример конфигурации будет использоваться для:

* подключения к PostgreSQL;
* подключения к MinIO;
* настройки encryption key;
* параметров приложения;
* TTL и других системных настроек.

---

## Run

### Development

Запусти приложение:

```bash
uv run fastapi dev app/main.py
```

После запуска:

```text
Application    http://localhost:8000
Swagger        http://localhost:8000/docs
```

### Infrastructure

Запуск PostgreSQL и MinIO:

```bash
docker compose up -d
```

### Full Docker environment

```bash
docker compose up --build
```

---

## API

Основные endpoints:

```text
POST   /api/secrets
GET    /api/secrets/{id}
GET    /api/secrets/{id}/download
DELETE /api/secrets/{id}

GET    /api/health
```

### Create secret

```text
POST /api/secrets
```

Создаёт новый временный секрет.

Поддерживаемые данные:

* текст;
* файл.

Параметры:

```text
TTL
Maximum downloads
File / text content
```

### Get secret

```text
GET /api/secrets/{id}
```

Возвращает доступный секрет или информацию о его недоступности.

### Download

```text
GET /api/secrets/{id}/download
```

Предоставляет файл и увеличивает счётчик использования.

После достижения `max_downloads` секрет становится недоступным.

### Delete

```text
DELETE /api/secrets/{id}
```

Удаляет секрет и связанные данные.

### Health

```text
GET /api/health
```

Проверяет состояние приложения.

---

## Swagger / OpenAPI

Интерактивная документация API доступна по адресу:

```text
http://localhost:8000/docs
```

OpenAPI schema:

```text
http://localhost:8000/openapi.json
```

---

## Tests

Запуск тестов:

```bash
uv run pytest
```

Планируемые группы тестов:

```text
test_secrets.py
    создание и получение секретов

test_encryption.py
    шифрование и расшифровка

test_expiration.py
    TTL и автоматическое истечение срока
```

---

## Migrations

Создание новой миграции:

```bash
uv run alembic revision --autogenerate -m "description"
```

Применение миграций:

```bash
uv run alembic upgrade head
```

---

## Roadmap

### Version 0.1 — Foundation

* [x] Python project initialization
* [x] uv configuration
* [x] FastAPI application
* [x] Jinja2 templates
* [x] Base layout
* [x] Web interface
* [x] Initial UI design
* [x] Basic navigation
* [x] Health-check endpoint
* [x] Swagger/OpenAPI

### Version 0.2 — Core

* [ ] PostgreSQL integration
* [ ] SQLAlchemy models
* [ ] Alembic migrations
* [ ] MinIO integration
* [ ] File upload
* [ ] Text secrets
* [ ] Encryption service
* [ ] UUID secret links
* [ ] TTL
* [ ] Download limits
* [ ] Secret destruction

### Version 0.3 — Reliability

* [ ] Cleanup worker
* [ ] Complete REST API
* [ ] Automated tests
* [ ] Error handling
* [ ] Input validation
* [ ] Rate limiting
* [ ] Logging
* [ ] Docker Compose integration

### Future

* [ ] Client-side encryption
* [ ] User accounts
* [ ] API keys
* [ ] Team workspaces
* [ ] CLI
* [ ] Production object storage
* [ ] Monitoring
* [ ] Billing
* [ ] SaaS deployment

---

## Project Goal

File Vault начинается как учебный проект для изучения разработки backend-сервисов на Python, работы с асинхронными API, базами данных, объектным хранилищем, криптографией и Docker.

При этом архитектура проекта изначально строится с возможностью дальнейшего развития в самостоятельный SaaS-продукт.

Основная идея остаётся простой:

> **Передать данные сейчас — не хранить их потом.**

---

## License

This project is developed as a study project with the possibility of further development into a commercial SaaS.