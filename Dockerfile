# Базовый образ, например, Python
FROM python:latest

WORKDIR /app

# Копирование requirements.txt и установка зависимостей
COPY apps/reporting_app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копирование кода приложения в контейнер
COPY ./apps/reporting_app /app

# Указание команды для запуска приложения через Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
