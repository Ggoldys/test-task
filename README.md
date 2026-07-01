# leads-service

FastAPI-сервис для обработки заявок с outbox pattern и Kafka.

## Технологии

- Python 3.12+
- FastAPI
- PostgreSQL + asyncpg + SQLAlchemy async
- Alembic (миграции)
- Redpanda (Kafka-compatible) через aiokafka

## Запуск

### 1. Поднять Redpanda

```bash
docker compose up -d
```
Создать топики (если не создались автоматически):

```bash
docker exec -it test-task-redpanda-1 rpk topic create leads.events.v1 lead_moderation.events.v1 -p 1 -r 1
```

### 2. Настройка окружения


```bash
cp .env.example .env
```
Отредактировать .env при необходимости


### 3. Применить миграции

```bash
alembic upgrade head
```

### 4. Запустить API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger: http://localhost:8000/docs

### 5. Запустить Outbox Publisher

```bash
python -m app.workers.outbox_publisher
```

### 6. Запустить Kafka Consumer

```bash
python -m app.workers.kafka_consumer
```

## Переменные окружения

| Переменная | Значение по умолчанию | Описание |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:1111@localhost:5433/test_leads` | Подключение к PostgreSQL |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:19092` | Адрес Kafka/Redpanda |
| `KAFKA_LEADS_TOPIC` | `leads.events.v1` | Топик для исходящих событий |
| `KAFKA_MODERATION_TOPIC` | `lead_moderation.events.v1` | Топик для входящих событий |
| `OUTBOX_POLL_INTERVAL` | `5` | Интервал опроса outbox (сек) |

## API

### POST /leads

Создание заявки:

```json
{
  "name": "Иван",
  "phone": "+79991234567",
  "source": "landing",
  "comment": "Хочу консультацию"
}
```

Ответ: `201 Created` с данными заявки, статус `new`.

### GET /leads/{lead_id}

Получение заявки по ID.

Ответ: `200 OK` с данными заявки.

Если заявка не найдена: `404` со структурированной ошибкой:

```json
{
  "error": {
    "code": "lead_not_found",
    "message": "Заявка не найдена",
    "correlation_id": "uuid"
  }
}
```

## Пример ручной отправки lead_created события

```bash
docker exec -it test-task-redpanda-1 rpk topic produce leads.events.v1
```
Ввести JSON и нажать Enter

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "lead_created.v1",
  "aggregate_id": "87dbacbf-7682-48be-b64c-b78f644a1476",
  "occurred_at": "2026-06-26T10:00:00Z",
  "payload": {
    "lead_id": "87dbacbf-7682-48be-b64c-b78f644a1476",
    "name": "Иван",
    "phone": "+79991234567",
    "source": "landing"
  }
}
```
## Пример ручной отправки moderation события

```bash
docker exec -it test-task-redpanda-1 rpk topic produce lead_moderation.events.v1
```

```json
{
  "event_id": "660e8400-e29b-41d4-a716-446655440001",
  "event_type": "lead_moderation_finished.v1",
  "aggregate_id": "87dbacbf-7682-48be-b64c-b78f644a1476",
  "occurred_at": "2026-06-26T10:05:00Z",
  "payload": {
    "lead_id": "70aafd2e-9bc2-409c-b8ec-a5bfaefbc159",
    "approved": true,
    "reason": null
  }
}
```

## Что сделано

- [x] POST /leads — сохранение заявки + outbox event в одной транзакции
- [x] GET /leads/{id} — получение заявки со структурированной ошибкой 404
- [x] Outbox publisher — чтение и публикация событий в Kafka
- [x] Kafka consumer — приём moderation-событий с идемпотентностью
- [x] Миграции Alembic
- [x] Docker Compose с Redpanda

## Что улучшить

- Логирование
- Unit/integration тесты