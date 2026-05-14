#!/bin/sh
set -e

DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
DB_NAME=${DB_NAME:-postgres}

echo "Waiting for database at $DB_HOST:$DB_PORT..."

# Ждём доступности БД
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is up - running migrations"
python manage.py migrate --noinput

# Собираем статику (если настроено STATIC_ROOT)
python manage.py collectstatic --noinput || true

# Создаём суперпользователя, если заданы переменные — выполняем безопасный inline Python
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  python - <<'PY'
import os
# Указываем модуль настроек перед django.setup()
# Замените 'rental_project.settings' на ваш модуль настроек, если он отличается.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rental_project.settings")
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
if username and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
PY
fi

exec "$@"