# Верховия — Backend для учёта медицинских отходов

Система управления партиями медицинских отходов: от образователя до переработчика.
Водитель получает доступ через QR-код, все действия логируются в журнале аудита.

---

## Обоснование технологий

**Django + Django REST Framework** выбран как основной фреймворк: он даёт ORM, систему миграций, встроенную авторизацию и админку из коробки, что критично для проекта с ролями и сложной моделью данных. DRF позволяет быстро строить REST API с сериализацией, валидацией и пермишенами.

**PostgreSQL** — реляционная БД с поддержкой JSON-полей, транзакций и внешних ключей. Данные о партиях, статусах и пользователях жёстко связаны между собой, поэтому реляционная модель здесь очевидный выбор. Миграции через Django делают схему воспроизводимой на любом окружении.

**JWT (Simple JWT)** — stateless-аутентификация, удобна для мобильного клиента и сканера QR-кодов: не нужно хранить сессии на сервере.

**Docker + docker-compose** — изолированное окружение, одна команда для запуска всего стека (backend + db). Упрощает онбординг и деплой.

---

## Что делает

- Образователь создаёт партию отходов и генерирует QR-код с настраиваемым сроком действия
- Водитель сканирует QR и видит: тип отходов, количество, адреса вывоза и доставки
- Переработчик подтверждает приём партии — финальная смена статуса
- Инспектор и администратор видят все записи системы
- Все действия пишутся в журнал аудита

---

## Как запустить

### Через Docker (рекомендуется)

```bash
git clone git@github.com:lenchikponchik/verhoviya_project.git
cd verhoviya_project
docker compose up --build -d
docker compose exec backend python manage.py migrate
```

Документация API: http://localhost:8001/api/docs/

### Локально

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # настрой переменные окружения
python manage.py migrate
python manage.py runserver
```

---

## Демо-пользователи

| Логин | Пароль | Роль |
|---|---|---|
| admin@example.com | admin12345 | Администратор |
| educator@example.com | educator12345 | Образователь |
| processor@example.com | processor12345 | Переработчик |
| driver@example.com | driver12345 | Водитель |

---

## Структура проекта

```
verhoviya_project/
├── apps/
│   ├── audit/          # Модель AuditLog — журнал всех действий
│   ├── batches/        # Партии отходов, статусы, QR-коды, лог сканирований
│   ├── organizations/  # Организации (ИНН, КПП)
│   └── users/          # Пользователи, роли, профили (водитель, образователь, переработчик)
├── config/             # Настройки Django (settings, urls, wsgi)
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── requirements.txt
```

---

## Архитектура

```
┌─────────────┐     JWT      ┌──────────────────┐
│   Клиент    │ ──────────▶  │   Django REST API │
│ (браузер /  │              │                  │
│  мобильный) │ ◀──────────  │  - auth          │
└─────────────┘   JSON       │  - batches       │
                             │  - organizations │
      QR-scan                │  - audit         │
┌─────────────┐              └────────┬─────────┘
│   Водитель  │ ──────────▶           │
│  (QR-код)   │                       │ ORM
└─────────────┘              ┌────────▼─────────┐
                             │   PostgreSQL     │
                             │                  │
                             │  user            │
                             │  othody          │
                             │  status          │
                             │  qr              │
                             │  qr_scan_log     │
                             │  audit_log       │
                             └──────────────────┘
```

**Поток данных:**
1. Пользователь логинится → получает JWT access + refresh токен
2. Образователь создаёт партию → автоматически создаётся запись статуса `CREATED`
3. Образователь генерирует QR с `expires_at` → водитель сканирует → `QRScanLog` фиксирует попытку
4. Водитель подтверждает передачу → статус меняется на `IN_TRANSIT`
5. Переработчик подтверждает приём → статус `ACCEPTED`, QR деактивируется
6. Каждое действие пишется в `AuditLog`

---

## API — эндпоинты и примеры

### Аутентификация

**POST /api/v1/auth/login**
```json
// Request
{ "login": "educator@example.com", "password": "educator12345" }

// Response 200
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

**GET /api/v1/auth/me**
```json
// Response 200
{
  "id": 2,
  "login": "educator@example.com",
  "full_name": "Иванов Иван Иванович",
  "role": "RECYCLER"
}
```

### Партии отходов

**POST /api/v1/batches/**
```json
// Request
{
  "waste_type": "Класс Б",
  "quantity": "12.50",
  "pickup_point": "ул. Ленина, 10",
  "delivery_point": 1,
  "qr_expires_hours": 48
}

// Response 201
{
  "id": 5,
  "waste_type": "Класс Б",
  "quantity": "12.50",
  "current_status": "CREATED",
  "qr": {
    "code": "a3f9c1d2",
    "expires_at": "2025-12-01T12:00:00Z",
    "is_active": true
  }
}
```

**GET /api/v1/batches/**
```json
// Response 200
[
  {
    "id": 5,
    "waste_type": "Класс Б",
    "quantity": "12.50",
    "current_status": "IN_TRANSIT",
    "pickup_point": "ул. Ленина, 10"
  }
]
```

**POST /api/v1/batches/{id}/status/**
```json
// Request
{ "state": "ACCEPTED" }

// Response 200
{ "id": 5, "state": "ACCEPTED", "time": "2025-11-30T09:15:00Z" }
```

**GET /api/v1/batches/{id}/qr/**
```json
// Response 200
{
  "code": "a3f9c1d2",
  "expires_at": "2025-12-01T12:00:00Z",
  "is_active": true,
  "waste": {
    "waste_type": "Класс Б",
    "quantity": "12.50",
    "pickup_point": "ул. Ленина, 10",
    "delivery_point": "ул. Заводская, 5"
  }
}
```

### Организации

**GET /api/v1/organizations/**
```json
[
  { "id": 1, "name": "МедЦентр №1", "inn": "7701234567", "kpp": "770101001" }
]
```

### Журнал аудита

**GET /api/v1/audit/**
```json
[
  {
    "id": 12,
    "action": "STATUS_CHANGED",
    "object_type": "Waste",
    "object_id": "5",
    "before": { "state": "CREATED" },
    "after": { "state": "IN_TRANSIT" },
    "created_at": "2025-11-30T08:00:00Z"
  }
]
```

---

## Статусы партии

| Статус | Описание |
|---|---|
| `CREATED` | Партия создана образователем |
| `IN_TRANSIT` | Водитель подтвердил вывоз |
| `DELIVERED` | Доставлена на площадку |
| `ACCEPTED` | Принята переработчиком |
| `CANCELLED` | Отменена |
