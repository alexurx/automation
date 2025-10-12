#!/bin/sh

# Устанавливаем переменные окружения, чтобы cron их "видел"
printenv | grep -v "no_proxy" >> /etc/environment

# Создаем файл логов, если его нет
touch /var/log/cron.log
chmod 666 /var/log/cron.log

echo "=== Starting cron daemon ==="

# Запускаем cron в режиме foreground, чтобы контейнер не завершался
exec cron -f