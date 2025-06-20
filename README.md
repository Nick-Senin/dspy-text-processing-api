# DSPy Text Processing API - Система Извлечения Преобразований

Система для извлечения и обработки преобразований из текста с использованием DSPy.

## Структура проекта

```
├── modules/                    # Основные модули системы
│   ├── extract.py             # Извлечение преобразований
│   ├── process.py             # Обработка и фильтрация
│   ├── enrich.py              # Обогащение связок
│   └── merge.py               # Слияние похожих преобразований
├── metrics/                   # Метрики оценки качества
│   ├── assess_banal.py        # Оценка банальности
│   ├── assess_reproducibility.py  # Оценка воспроизводимости
│   ├── assess_similarity.py   # Оценка схожести
│   ├── assess_detail.py       # Оценка детализации
│   └── combined.py            # Комбинированная метрика
├── server/                    # Flask веб-сервер
│   ├── app.py                 # Основной Flask сервер
│   ├── test_server.py         # Тестирование сервера
│   ├── example_request.py     # Пример использования API
│   └── README_FLASK.md        # Документация сервера
├── main.py                    # Основной скрипт обработки
├── run_server.py              # Запуск Flask сервера
├── config.py                  # Конфигурация
├── requirements.txt           # Зависимости
├── Dockerfile                 # Docker образ для развертывания
├── docker-compose.yml         # Docker Compose конфигурация
├── DEPLOYMENT.md              # Руководство по развертыванию
└── demonstrations.json        # Примеры для обучения
```

## Установка

1. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Настройте переменные окружения:**
   Создайте файл `.env` с необходимыми API ключами.

## Использование

### 1. Консольная обработка

Обработка одного текста:
```bash
python main.py
```

Валидация на тестовом наборе:
```bash
python main.py --validate
```

### 2. Flask веб-сервер

Запуск сервера:
```bash
python run_server.py
```

Или напрямую:
```bash
python server/app.py
```

Тестирование API:
```bash
python server/test_server.py
```

Пример использования:
```bash
python server/example_request.py
```

### 3. API Эндпоинт

**POST** `/process` - Обработка текста

**Вход:**
```json
{
    "text": "Ваш текст для обработки",
    "banal_threshold": 0.6,
    "reproducibility_threshold": 0.7
}
```

**Выход:**
```json
{
    "success": true,
    "unfiltered_triplets": [...],
    "failed_reasoning": "...",
    "processed_count": 2,
    "total_count": 5
}
```

## Основные компоненты

### Модуль process_text
Основная функция обработки, которая:
- Извлекает связки из текста
- Фильтрует по банальности
- Обогащает прошедшие фильтр связки
- Фильтрует по воспроизводимости
- Возвращает неотфильтрованные связки и детали отфильтрованных

### Flask сервер
Предоставляет REST API для обработки текста с настраиваемыми фильтрами.

### Метрики качества
- **Банальность**: Оценивает, насколько тривиальны извлеченные преобразования
- **Воспроизводимость**: Проверяет, можно ли воспроизвести преобразование
- **Схожесть**: Измеряет схожесть между связками
- **Детализация**: Оценивает детальность описания

## Документация

- **Flask сервер**: `server/README_FLASK.md`
- **Конфигурация**: `config.py`
- **Примеры**: `demonstrations.json`

## Требования

- Python 3.8+
- DSPy
- Flask (для веб-сервера)
- OpenAI API ключ
- Файл `optimized_extractor.pkl` (создается автоматически при первом запуске)