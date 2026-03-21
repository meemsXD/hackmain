# Frontend MVP (React + TypeScript + Vite)

Frontend-часть для проекта учета медицинских отходов класса «Г».  
Реализована отдельно от backend, как SPA, с ролевой навигацией и подключением к REST API.

## Стек

- React + TypeScript + Vite
- React Router
- Axios
- TanStack Query
- React Hook Form + Zod
- Tailwind CSS
- date-fns
- react-qr-code

## Быстрый запуск

1. Перейти в папку фронта:

```bash
cd frontend
```

2. Создать env:

```bash
cp .env.example .env
```

3. Установить зависимости и запустить:

```bash
npm install
npm run dev
```

По умолчанию фронт: `http://localhost:5173`.

## Docker-сборка

```bash
cd frontend
docker build -t waste-frontend .
docker run --rm -p 5174:80 waste-frontend
```

## Конфигурация окружения

`.env`:

- `VITE_API_BASE_URL` — адрес API (`http://localhost:8001/api/v1`)
- `VITE_ADMIN_URL` — ссылка на backend admin (`http://localhost:8001/admin/`)

## Реализованные маршруты

Публичные:

- `/login`
- `/register`
- `/driver-access/:token`

Защищенные:

- `/app/profile`
- `/app/profile/roles`
- `/app/educator/batches`
- `/app/educator/batches/new`
- `/app/educator/batches/:id`
- `/app/educator/reports`
- `/app/driver/access`
- `/app/driver/batches`
- `/app/driver/batches/:id`
- `/app/processor/batches`
- `/app/processor/batches/:id`
- `/app/processor/drivers`
- `/app/inspector/journal`
- `/app/inspector/reports`

## Что важно учесть

- Фронт не изменяет backend и БД.
- Для отсутствующих в backend endpoint-ов (роль-заявки, полноценный чат, часть отчетов) добавлены безопасные fallback-сценарии на клиенте.
- Критичные действия (отмена, забор, доставка, приемка) требуют токен подписи через отдельный модальный поток.
- Все основные экраны имеют состояния `loading/error/empty/success`.
