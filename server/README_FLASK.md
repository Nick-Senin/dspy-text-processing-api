# 🚀 Flask API для обработки текста

Этот Flask сервер предоставляет API для обработки текста с использованием DSPy и извлечения связок трансформации.

## 📁 Структура файлов

```
server/
├── app.py                 # Основной Flask сервер
├── test_server.py         # Скрипт для тестирования API
├── example_request.py     # Примеры использования API
├── curl_examples.md       # Примеры curl запросов
└── README_FLASK.md        # Эта документация
```

## 🛠️ Установка и запуск

### Из корневой папки проекта:
```bash
# Запуск сервера
python run_server.py

# Или напрямую
python server/app.py
```

### Из папки server:
```bash
cd server
python app.py
```

## 🌐 API Эндпоинты

### 1. `GET /` - Главная страница
Возвращает информацию об API и примеры использования.

**Пример ответа:**
```json
{
  "message": "Flask сервер для обработки текста",
  "endpoints": {
    "/process": "POST - Обработка текста с фильтрацией",
    "/health": "GET - Проверка состояния сервера"
  },
  "example_request": {
    "url": "/process",
    "method": "POST",
    "body": {
      "text": "Ваш текст для обработки...",
      "banal_threshold": 0.6,
      "reproducibility_threshold": 0.7
    }
  }
}
```

### 2. `GET /health` - Проверка состояния
Проверяет, работает ли сервер и загружен ли экстрактор.

**Пример ответа:**
```json
{
  "status": "healthy",
  "extractor_loaded": true
}
```

### 3. `POST /process` - Обработка текста
Основной эндпоинт для обработки текста.

**Параметры запроса:**
```json
{
  "text": "Текст для обработки (обязательно)",
  "banal_threshold": 0.6,  // Порог фильтрации по банальности (опционально)
  "reproducibility_threshold": 0.7  // Порог воспроизводимости (опционально)
}
```

**Пример ответа:**
```json
{
  "success": true,
  "message": "Обработка завершена успешно",
  "filtered_triplets": [
    {
      "initial_state": "Человек сталкивается с проблемой",
      "transformation": "применяет новый подход",
      "result": "получает эффективное решение"
    }
  ],
  "unfiltered_triplets": [
    {
      "initial_state": "Человек сталкивается с проблемой",
      "transformation": "применяет новый подход",
      "result": "получает эффективное решение"
    },
    {
      "initial_state": "Проблема требует решения",
      "transformation": "используется стандартный метод",
      "result": "получается обычный результат"
    }
  ],
  "failed_reasoning": "Связка 2: Банальность 0.8 > 0.6 (порог). LLM объяснение: Эта связка представляет очень стандартную ситуацию...",
  "processed_count": 1,
  "total_count": 2
}
```

## 🧪 Тестирование

### Автоматическое тестирование
```bash
python server/test_server.py
```

### Демонстрационные примеры
```bash
python server/example_request.py
```

### Ручное тестирование с curl
См. файл `curl_examples.md` для подробных примеров.

## ⚙️ Конфигурация

Сервер использует настройки из файла `config.py` в корне проекта:
- `MAIN_MODEL` - основная модель для извлечения связок
- `BANAL_MODEL` - модель для оценки банальности
- `BANAL_THRESHOLD` - порог банальности по умолчанию
- API ключи для OpenRouter

## 🔧 Технические детали

### Инициализация
- При первом запросе сервер загружает оптимизированный экстрактор из `optimized_extractor.pkl`
- Настраивает DSPy с указанными моделями
- Экстрактор кэшируется в памяти для последующих запросов

### Обработка ошибок
- Валидация входных данных
- Обработка ошибок JSON
- Проверка типов данных для порогов
- Graceful handling исключений DSPy

### Производительность
- Первый запрос может занять больше времени из-за инициализации
- Последующие запросы обрабатываются быстрее
- Время обработки зависит от длины текста и сложности

## 🌍 Развертывание с ngrok

Для публичного доступа к API:

```bash
# Установка ngrok (если не установлен)
pip install pyngrok

# Запуск с ngrok
python run_with_ngrok.py
```

Это создаст публичный URL для доступа к API из любой точки интернета.

## 📝 Примеры использования

### Python requests
```python
import requests

data = {
    "text": "Человек решает проблему. Он применяет новый подход.",
    "banal_threshold": 0.6,
    "reproducibility_threshold": 0.7
}

response = requests.post(
    "http://localhost:5000/process",
    json=data
)

result = response.json()
print(f"Обработано: {result['processed_count']} из {result['total_count']}")
```

### JavaScript fetch
```javascript
fetch('http://localhost:5000/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'Человек решает проблему. Он применяет новый подход.',
    banal_threshold: 0.6,
    reproducibility_threshold: 0.7
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## ⚠️ Важные замечания

1. **Первый запуск**: Убедитесь, что файл `optimized_extractor.pkl` существует. Если нет, запустите `main.py` для его создания.

2. **Переменные окружения**: Создайте файл `.env` с необходимыми API ключами.

3. **Зависимости**: Установите все зависимости из `requirements.txt`.

4. **Производительность**: Для продакшена рекомендуется использовать WSGI сервер (например, Gunicorn).

5. **Безопасность**: В продакшене добавьте аутентификацию и rate limiting.