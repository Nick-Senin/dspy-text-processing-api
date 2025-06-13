# Примеры curl запросов к API

## 🌐 URL сервера
```
https://081d-138-68-156-65.ngrok-free.app
```

## 📋 Проверка состояния сервера

### Windows PowerShell
```powershell
Invoke-RestMethod -Uri "https://081d-138-68-156-65.ngrok-free.app/health"
```

### Linux/Mac/WSL
```bash
curl https://081d-138-68-156-65.ngrok-free.app/health
```

## 📝 Обработка текста

### Windows PowerShell (рекомендуется)
```powershell
$body = @{
    text = "Человек решает проблему. Он применяет новый подход. Получается хороший результат."
    banal_threshold = 0.6
    reproducibility_threshold = 0.7
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://081d-138-68-156-65.ngrok-free.app/process" -Method POST -ContentType "application/json" -Body $body
```

### Linux/Mac/WSL
```bash
curl -X POST https://081d-138-68-156-65.ngrok-free.app/process \
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
curl -X POST https://081d-138-68-156-65.ngrok-free.app/process \
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

Invoke-RestMethod -Uri "https://081d-138-68-156-65.ngrok-free.app/process" -Method POST -ContentType "application/json" -Body $body
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
3. **ngrok URL изменился** - проверьте актуальный URL в консоли сервера