# Waste MVP Backend

## Установка

### 1. Клонируй репозиторий
```bash
git clone git@github.com:lenchikponchik/verhoviya_project.git
cd verhoviya_project
```

### 2. Запусти через Docker
```bash
docker compose up --build -d
```

### 3. Проверь что работает
```bash
docker compose ps
docker compose logs backend
```

### 4. Открой документацию API
```
http://localhost:8001/api/docs/
```

## Демо-пользователи
| Email | Пароль | Роль |
|-------|--------|------|
| admin@example.com | admin12345 | Администратор |
| educator@example.com | educator12345 | Образователь |
| processor@example.com | processor12345 | Переработчик |
| driver@example.com | driver12345 | Водитель |

## Таблицы БД
| Таблица | Описание |
|---------|----------|
| user | Пользователи системы |
| driver_profile | Профили водителей (номер ТС) |
| organization | Организации (ИНН, КПП) |
| educator_profile | Профили образователей |
| processor_profile | Профили переработчиков |
| waste_batch | Партии отходов |
| batch_status | История статусов партий |
| qr_token | QR-токены доступа |
| audit_log | Журнал событий |

## API эндпоинты
- POST /api/v1/auth/register — регистрация
- POST /api/v1/auth/login — вход
- GET  /api/v1/auth/me — текущий пользователь
- GET/POST /api/v1/batches/ — партии отходов
- POST /api/v1/batches/{id}/status/ — изменить статус
- GET  /api/v1/batches/{id}/qr/ — QR-токен партии
- GET  /api/v1/organizations/ — организации
- GET  /api/v1/audit/ — журнал событий
