import dspy
import os
from dotenv import load_dotenv

# Основная модель для извлечения и обогащения
MAIN_MODEL = "openrouter/openai/gpt-4.1"
BANAL_MODEL = "openrouter/google/gemini-2.0-flash-001"
ASSESSMENT_MODEL = 'openrouter/openai/gpt-4.1-mini'

MAIN_MODEL_MAX_TOKENS = 4096
MAIN_MODEL_TEMPERATURE = 0.0

# Порог банальности
BANAL_THRESHOLD = 0.6

# Ключ API для OpenRouter
load_dotenv()
OPENROUTER_API_KEY = "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" 

def get_assessment_lm():

    """Инициализирует и возвращает языковую модель для оценки метрик."""

    return dspy.LM(
        model=ASSESSMENT_MODEL,
        api_key=OPENROUTER_API_KEY,
        api_base='https://openrouter.ai/api/v1',
        max_tokens=1000  # Ограничение для оценочных задач
    )