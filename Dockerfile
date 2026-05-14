FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Системные зависимости для сборки и работы psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и ставим зависимости
COPY requirements.txt /code/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt

# Копируем проект (как root)
COPY . /code/

# Копируем entrypoint и делаем его исполняемым (как root)
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Создадим не-root пользователя и отдадим ему права на код и entrypoint
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /code /entrypoint.sh

# Переключаемся на непользовательского пользователя
USER appuser

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "rental_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]