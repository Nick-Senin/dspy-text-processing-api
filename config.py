import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# OpenRouter API ключ
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Модели
MAIN_MODEL = os.getenv('MAIN_MODEL', 'openrouter/openai/gpt-4.1')
BANAL_MODEL = os.getenv('BANAL_MODEL', 'openrouter/google/gemini-2.0-flash-001')
ASSESSMENT_MODEL = os.getenv('ASSESSMENT_MODEL', 'openrouter/openai/gpt-4.1-mini')

# Настройки основной модели
MAIN_MODEL_MAX_TOKENS = 4000
MAIN_MODEL_TEMPERATURE = 0.0

# Пороги
BANAL_THRESHOLD = float(os.getenv('BANAL_THRESHOLD', '0.6'))

# Проверка наличия API ключа
if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY не найден в переменных окружения. "
        "Создайте файл .env и добавьте: OPENROUTER_API_KEY=ваш_ключ"
    )