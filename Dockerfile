# syntax=docker/dockerfile:1.4

# ============================================================================
# Multi-stage Dockerfile для DSPy Text Processing API
# Оптимизирован для production развертывания на Coolify
# ============================================================================

ARG PYTHON_VERSION=3.11.9
ARG APP_ENV=production

# ============================================================================
# Stage 1: Build dependencies (builder stage)
# ============================================================================
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# Установка переменных окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Копирование и установка Python зависимостей
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Production runtime (final stage)
# ============================================================================
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

# Метаданные образа
LABEL maintainer="DSPy Text Processing API" \
      description="Flask API для обработки текста с использованием DSPy" \
      version="1.0.0"

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=server/app.py \
    FLASK_ENV=production \
    PYTHONPATH=/app

# Создание пользователя без привилегий
ARG APP_USER=appuser
ARG APP_USER_UID=1001
RUN groupadd --gid $APP_USER_UID $APP_USER && \
    useradd --uid $APP_USER_UID --gid $APP_USER --shell /bin/bash --create-home $APP_USER

# Установка рабочей директории
WORKDIR /app

# Копирование виртуального окружения из builder stage
COPY --from=builder --chown=$APP_USER:$APP_USER $VIRTUAL_ENV $VIRTUAL_ENV

# Копирование исходного кода приложения
COPY --chown=$APP_USER:$APP_USER . .

# Создание необходимых директорий и установка прав
RUN mkdir -p /app/logs /app/tmp && \
    chown -R $APP_USER:$APP_USER /app

# Переключение на непривилегированного пользователя
USER $APP_USER

# Проверка работоспособности
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

# Открытие порта
EXPOSE 5000

# Команда запуска приложения
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--worker-class", "sync", "--worker-tmp-dir", "/dev/shm", "server.app:app"]