FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
CMD ["bash", "-lc", "python manage.py makemigrations users organizations batches audit && python manage.py migrate && (python manage.py seed_demo || true) && gunicorn config.wsgi:application --bind 0.0.0.0:8001"]
