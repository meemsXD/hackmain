# Быстрый запуск (без потери аккаунтов)

## 1) Запустить Postgres с постоянным volume

```bash
cd /mnt/c/Users/vsmyk/Downloads/project/verhoviya_project
./scripts/start_postgres.sh
```

Важно:
- Не удаляйте контейнер `waste-db` через `docker rm -f`.
- Для остановки используйте `docker stop waste-db`.
- Для повторного запуска используйте `docker start waste-db`.

## 2) Запустить backend

```bash
cd /mnt/c/Users/vsmyk/Downloads/project/verhoviya_project
source .venv_linux/bin/activate
cp .env.example .env 2>/dev/null || true
python manage.py migrate
python manage.py ensure_admin_access --set-superuser
python manage.py seed_demo
python manage.py runserver 0.0.0.0:8001
```

## 3) Запустить frontend

```bash
cd /mnt/c/Users/vsmyk/Downloads/project/verhoviya_project/frontend
cp .env.example .env 2>/dev/null || true
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## Адреса

- Frontend: http://localhost:5173
- Admin: http://localhost:8001/admin/
- API docs: http://localhost:8001/api/docs/

## Логин в админку

- `admin@example.com` / `admin12345`
