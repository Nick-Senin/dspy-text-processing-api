from flask import Flask, request, jsonify
import dspy
from dotenv import load_dotenv
import os
import sys
import logging

# Добавляем родительскую папку в путь Python для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Подавляем предупреждения DSPy о structured output format
logging.getLogger("dspy").setLevel(logging.WARNING)

import config
from modules.extract import TransformationExtractor
from modules.process import process_text

# Загрузка переменных окружения из .env файла
load_dotenv()

# --- Constants ---
OPTIMIZED_EXTRACTOR_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "optimized_extractor.pkl")

app = Flask(__name__)

# Глобальная переменная для хранения экстрактора
extractor = None

def setup_dspy():
    """Configures the DSPy language models."""
    main_lm = dspy.LM(
        model=config.MAIN_MODEL,
        api_key=config.OPENROUTER_API_KEY,
        api_base='https://openrouter.ai/api/v1',
        max_tokens=config.MAIN_MODEL_MAX_TOKENS,
        temperature=config.MAIN_MODEL_TEMPERATURE
    )
    
    banal_lm = dspy.LM(
        model=config.BANAL_MODEL,
        api_key=config.OPENROUTER_API_KEY,
        api_base='https://openrouter.ai/api/v1',
        max_tokens=500,
        temperature=0.0
    )

    # Configure both language models. The first one is the default.
    dspy.configure(lm=main_lm, banal_lm=banal_lm)

def load_extractor():
    """Loads the pre-optimized extractor."""
    if not os.path.exists(OPTIMIZED_EXTRACTOR_PATH):
        raise FileNotFoundError(f"Оптимизированный экстрактор не найден по пути {OPTIMIZED_EXTRACTOR_PATH}")
    
    print("Загрузка оптимизированного экстрактора...")
    optimized_extractor = TransformationExtractor()
    optimized_extractor.load(OPTIMIZED_EXTRACTOR_PATH)
    print("Загрузка завершена.")
    return optimized_extractor

def initialize():
    """Инициализация экстрактора."""
    global extractor
    if extractor is None:
        setup_dspy()
        extractor = load_extractor()

@app.route('/process', methods=['POST'])
def process_endpoint():
    """
    Эндпоинт для обработки текста.
    
    Принимает JSON с полями:
    - text: исходный текст для обработки
    - banal_threshold: порог фильтрации по банальности (опционально, по умолчанию из config)
    - reproducibility_threshold: порог фильтрации по воспроизводимости (опционально, по умолчанию 0.7)
    
    Возвращает JSON с полями:
    - filtered_triplets: массив связок, прошедших все фильтры
    - unfiltered_triplets: массив всех извлеченных связок
    - failed_reasoning: строка с рассуждениями для отфильтрованных связок
    - success: булево значение успешности операции
    - message: сообщение об ошибке (если есть)
    """
    try:
        # Инициализируем экстрактор при необходимости
        initialize()

        # Получаем данные из запроса
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Не предоставлены данные JSON',
                'filtered_triplets': [],
                'unfiltered_triplets': [],
                'failed_reasoning': ''
            }), 400

        # Извлекаем параметры
        text = data.get('text')
        if not text:
            return jsonify({
                'success': False,
                'message': 'Поле "text" обязательно',
                'filtered_triplets': [],
                'unfiltered_triplets': [],
                'failed_reasoning': ''
            }), 400

        banal_threshold = data.get('banal_threshold', config.BANAL_THRESHOLD)
        reproducibility_threshold = data.get('reproducibility_threshold', 0.7)

        # Валидация пороговых значений
        try:
            banal_threshold = float(banal_threshold)
            reproducibility_threshold = float(reproducibility_threshold)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Пороговые значения должны быть числами',
                'filtered_triplets': [],
                'unfiltered_triplets': [],
                'failed_reasoning': ''
            }), 400

        # Обрабатываем текст
        final_triplets, unfiltered_triplets, failed_reasoning = process_text(
            extractor, 
            text, 
            banal_threshold=banal_threshold, 
            reproducibility_threshold=reproducibility_threshold
        )

        return jsonify({
            'success': True,
            'message': 'Обработка завершена успешно',
            'filtered_triplets': final_triplets,
            'unfiltered_triplets': unfiltered_triplets,
            'failed_reasoning': failed_reasoning,
            'processed_count': len(final_triplets),
            'total_count': len(unfiltered_triplets)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Ошибка при обработке: {str(e)}',
            'filtered_triplets': [],
            'unfiltered_triplets': [],
            'failed_reasoning': ''
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка состояния сервера."""
    return jsonify({
        'status': 'healthy',
        'extractor_loaded': extractor is not None
    })

@app.route('/', methods=['GET'])
def index():
    """Главная страница с информацией об API."""
    return jsonify({
        'message': 'Flask сервер для обработки текста',
        'endpoints': {
            '/process': 'POST - Обработка текста с фильтрацией',
            '/health': 'GET - Проверка состояния сервера'
        },
        'example_request': {
            'url': '/process',
            'method': 'POST',
            'body': {
                'text': 'Ваш текст для обработки...',
                'banal_threshold': 0.6,
                'reproducibility_threshold': 0.7
            }
        },
        'example_response': {
            'success': True,
            'filtered_triplets': ['связки, прошедшие все фильтры'],
            'unfiltered_triplets': ['все извлеченные связки'],
            'failed_reasoning': 'детали отфильтрованных связок',
            'processed_count': 2,
            'total_count': 5
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)