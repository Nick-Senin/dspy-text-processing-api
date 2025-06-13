# Примеры curl запросов к API

## 🌐 URL сервера
```
http://localhost:5000
```

## 📋 Проверка состояния сервера

### Windows PowerShell
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health"
```

### Linux/Mac/WSL
```bash
curl http://localhost:5000/health
```

## 📝 Обработка текста

### Windows PowerShell (рекомендуется)
```powershell
$body = @{
    text = "Человек решает проблему. Он применяет новый подход. Получается хороший результат."
    banal_threshold = 0.6
    reproducibility_threshold = 0.7
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/process" -Method POST -ContentType "application/json" -Body $body
```

### Linux/Mac/WSL
```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Человек решает проблему. Он применяет новый подход. Получается хороший результат.",
    "banal_threshold": 0.6,
    "reproducibility_threshold": 0.7
  }'
```

### Альтернативный способ для Linux/Mac (из файла)
Создайте файл `request.json`:
```json
{
  "text": "Человек решает проблему. Он применяет новый подход. Получается хороший результат.",
  "banal_threshold": 0.6,
  "reproducibility_threshold": 0.7
}
```

Затем выполните:
```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d @request.json
```

## 🧪 Тестовый запрос с более длинным текстом

### Windows PowerShell
```powershell
$body = @{
    text = "Когда человек сталкивается с проблемой, он часто пытается решить её привычными способами. Однако иногда требуется изменить подход к решению проблемы. Применение нового метода может привести к неожиданному и эффективному результату."
    banal_threshold = 0.5
    reproducibility_threshold = 0.6
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/process" -Method POST -ContentType "application/json" -Body $body
```

## 📊 Ожидаемый ответ
```json
{
  "success": true,
  "message": "Обработка завершена успешно",
  "filtered_triplets": [
    {
      "initial_state": "...",
      "transformation": "...",
      "result": "..."
    }
  ],
  "unfiltered_triplets": [
    {
      "initial_state": "...",
      "transformation": "...",
      "result": "..."
    }
  ],
  "failed_reasoning": "...",
  "processed_count": 1,
  "total_count": 2
}
```

## ⚠️ Частые ошибки

1. **JSON parsing error** - убедитесь, что JSON корректно экранирован
2. **Connection timeout** - увеличьте timeout до 30-60 секунд
3. **Сервер не запущен** - убедитесь, что Flask сервер запущен на порту 5000