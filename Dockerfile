# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем cron и другие утилиты
RUN apt-get update && apt-get install -y cron

# Копируем скрипт и устанавливаем зависимости
COPY lab03/currency_exchange_rate.py .
RUN pip install --no-cache-dir requests

# Настраиваем cron
# Копируем файл с задачами
COPY lab03/cronjob /etc/cron.d/currency-cron

# Даем правильные права файлу с задачами
RUN chmod 0644 /etc/cron.d/currency-cron

# Копируем и делаем исполняемым entrypoint-скрипт
COPY lab03/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Запускаем entrypoint при старте контейнера
ENTRYPOINT ["/entrypoint.sh"]