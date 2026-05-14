FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code


RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /code/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt


COPY . /code/


COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /code /entrypoint.sh


USER appuser

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "rental_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]