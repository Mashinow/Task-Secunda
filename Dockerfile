# ---------------------------------------------------------------------------
# Базовый образ
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS base

WORKDIR /workdir
ENV PYTHONPATH=/workdir

# Минимальные системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Стадия миграций
# ---------------------------------------------------------------------------
FROM base AS migrate

# Копируем исходники и конфиг alembic
COPY alembic.ini .
COPY alembic/ alembic/
COPY app/ app/

# Точка входа — запуск миграций
ENTRYPOINT ["alembic"]
CMD ["upgrade", "head"]

FROM base AS runtime

# Копируем исходники
COPY app/ app/
COPY alembic.ini .
COPY alembic/ alembic/
COPY app/static/index.html static/index.html

# Порт приложения
EXPOSE 8000

# Создаём непривилегированного пользователя
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /data \
    && chown appuser:appuser /data
USER appuser

ENTRYPOINT ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]

# Пользовательский healthcheck
HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
  CMD curl -sf http://localhost:8000/docs > /dev/null || exit 1
