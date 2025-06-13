# 🚀 Развертывание DSPy Text Processing API на Coolify

Это руководство поможет вам развернуть DSPy Text Processing API на платформе Coolify.

## 📋 Предварительные требования

1. **Coolify сервер** - настроенный и работающий экземпляр Coolify
2. **GitHub репозиторий** - код должен быть загружен в GitHub
3. **OpenRouter API ключ** - для доступа к языковым моделям
4. **Docker** - для локального тестирования (опционально)

## 🔧 Настройка переменных окружения

В Coolify настройте следующие переменные окружения:

### Обязательные переменные:
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
FLASK_ENV=production
PYTHONPATH=/app
```

### Опциональные переменные:
```bash
# Настройки моделей (по умолчанию используются значения из config.py)
MAIN_MODEL=openrouter/openai/gpt-4.1
BANAL_MODEL=openrouter/google/gemini-2.0-flash-001
ASSESSMENT_MODEL=openrouter/openai/gpt-4.1-mini

# Пороги фильтрации
BANAL_THRESHOLD=0.6

# Настройки Gunicorn
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=120
```

## 🐳 Конфигурация Coolify

### 1. Создание нового приложения

1. Войдите в панель управления Coolify
2. Нажмите "New Resource" → "Application"
3. Выберите "Public Repository"
4. Укажите URL вашего GitHub репозитория: `https://github.com/Nick-Senin/dspy-text-processing-api`

### 2. Настройка сборки

В разделе "Build Configuration":

- **Build Pack**: `Dockerfile`
- **Dockerfile Location**: `./Dockerfile`
- **Build Context**: `.`
- **Target Stage**: `production`

### 3. Настройка сети

- **Port**: `5000`
- **Protocol**: `HTTP`
- **Health Check Path**: `/health`

### 4. Настройка ресурсов

Рекомендуемые настройки ресурсов:

- **CPU Limit**: `2 cores`
- **Memory Limit**: `1GB`
- **CPU Reservation**: `0.5 cores`
- **Memory Reservation**: `512MB`

### 5. Переменные окружения

Добавьте все необходимые переменные окружения в разделе "Environment Variables".

## 🔍 Проверка развертывания

После успешного развертывания проверьте работоспособность:

### 1. Health Check
```bash
curl https://your-app-url.coolify.io/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "extractor_loaded": true
}
```

### 2. API Information
```bash
curl https://your-app-url.coolify.io/
```

### 3. Тестовый запрос
```bash
curl -X POST https://your-app-url.coolify.io/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Человек решает проблему. Он применяет новый подход. Получается хороший результат.",
    "banal_threshold": 0.6,
    "reproducibility_threshold": 0.7
  }'
```

## 🔧 Локальное тестирование Docker образа

Перед развертыванием на Coolify рекомендуется протестировать локально:

### 1. Сборка образа
```bash
docker build -t dspy-text-api .
```

### 2. Запуск контейнера
```bash
docker run -d \
  --name dspy-api-test \
  -p 5000:5000 \
  -e OPENROUTER_API_KEY=your_api_key \
  -e FLASK_ENV=production \
  dspy-text-api
```

### 3. Тестирование
```bash
# Health check
curl http://localhost:5000/health

# API test
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Тестовый текст для обработки"}'
```

### 4. Очистка
```bash
docker stop dspy-api-test
docker rm dspy-api-test
```

## 🐳 Использование Docker Compose

Для локальной разработки и тестирования:

### Production режим:
```bash
docker-compose up api
```

### Development режим:
```bash
docker-compose --profile dev up api-dev
```

## 📊 Мониторинг и логи

### Просмотр логов в Coolify:
1. Перейдите в раздел "Logs" вашего приложения
2. Выберите нужный контейнер
3. Просматривайте логи в реальном времени

### Основные метрики для мониторинга:
- **CPU Usage** - должно быть < 80%
- **Memory Usage** - должно быть < 80%
- **Response Time** - должно быть < 30 секунд для обычных запросов
- **Error Rate** - должно быть < 1%

## 🔧 Устранение неполадок

### Проблема: Контейнер не запускается
**Решение**: Проверьте логи сборки и убедитесь, что все переменные окружения настроены правильно.

### Проблема: API возвращает 500 ошибку
**Решение**: 
1. Проверьте, что `OPENROUTER_API_KEY` настроен правильно
2. Убедитесь, что файл `optimized_extractor.pkl` создается при первом запуске
3. Проверьте логи приложения

### Проблема: Медленная обработка запросов
**Решение**:
1. Увеличьте количество Gunicorn workers
2. Увеличьте лимиты CPU и памяти
3. Проверьте настройки timeout

### Проблема: Health check не проходит
**Решение**:
1. Убедитесь, что приложение слушает на порту 5000
2. Проверьте, что эндпоинт `/health` доступен
3. Увеличьте timeout для health check

## 🔄 Обновление приложения

1. Внесите изменения в код
2. Сделайте commit и push в GitHub
3. В Coolify нажмите "Deploy" для пересборки и развертывания

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в Coolify
2. Убедитесь, что все переменные окружения настроены
3. Протестируйте локально с помощью Docker
4. Обратитесь к документации Coolify

## 🔗 Полезные ссылки

- [Документация Coolify](https://coolify.io/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Flask Production Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)