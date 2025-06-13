import dspy
from dotenv import load_dotenv
import os
import json
import sys
import argparse
import logging

# Подавляем предупреждения DSPy о structured output format
logging.getLogger("dspy").setLevel(logging.WARNING)

from dspy.teleprompt import BootstrapFewShot

import config
from modules.extract import TransformationExtractor
from modules.merge import TransformationMerger
from modules.process import process_text
from metrics.combined import combined_metric


# --- Constants ---
OPTIMIZED_EXTRACTOR_PATH = "optimized_extractor.pkl"
DEMONSTRATIONS_PATH = "demonstrations.json"
VALIDATION_TESTSET_PATH = "validation_testset.json"


# Загрузка переменных окружения из .env файла
load_dotenv()

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
        max_tokens=500, # As it was in assess_banal.py
        temperature=0.0
    )

    # Configure both language models. The first one is the default.
    dspy.configure(lm=main_lm, banal_lm=banal_lm)

def load_demonstrations(path):
    """Loads demonstrations from a JSON file and creates a trainset."""
    with open(path, 'r', encoding='utf-8') as f:
        demos_data = json.load(f)
    
    trainset = []
    for item in demos_data:
        example = dspy.Example(
            initial_text=item['initial_text'],
            transformations=item['transformations'],
        ).with_inputs('initial_text')
        trainset.append(example)
    return trainset

def load_or_train_extractor(extractor_path, demonstrations_path):
    """Loads a pre-optimized extractor or trains a new one."""
    if os.path.exists(extractor_path):
        print("Загрузка ранее оптимизированного экстрактора...")
        optimized_extractor = TransformationExtractor()
        optimized_extractor.load(extractor_path)
        print("Загрузка завершена.")
    else:
        trainset = load_demonstrations(demonstrations_path)
        optimizer = BootstrapFewShot(metric=combined_metric, max_bootstrapped_demos=3)
        
        print("Запуск оптимизации экстрактора преобразований...")
        optimized_extractor = optimizer.compile(TransformationExtractor(), trainset=trainset)
        print("Оптимизация завершена.")

        print(f"Сохранение оптимизированного экстрактора в {extractor_path}...")
        optimized_extractor.save(extractor_path)
        print("Сохранение завершено.")
    return optimized_extractor

def run_validation_testset(optimized_extractor):
    """
    Прогоняет все тексты из validation_testset.json через полный цикл обработки.
    """
    with open(VALIDATION_TESTSET_PATH, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    test_texts = data.get("validation_testset", [])
    print(f"\n=== Валидационный тестовый сет: {len(test_texts)} текстов ===\n")
    for idx, text in enumerate(test_texts, 1):
        print(f"\n--- Текст {idx} ---")
        print(text[:300] + ("..." if len(text) > 300 else ""))
        
        final, unfiltered, failed = process_text(optimized_extractor, text)
        print(f"  Извлечено {len(unfiltered)} связок, прошло фильтры: {len(final)}.")
        if failed:
            print("  Детали отфильтрованных связок:")
            print(failed)

def main():
    parser = argparse.ArgumentParser(description="Run transformation extractor.")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validation on the testset instead of the default text."
    )
    args = parser.parse_args()
    
    setup_dspy()
    
    optimized_extractor = load_or_train_extractor(
        OPTIMIZED_EXTRACTOR_PATH,
        DEMONSTRATIONS_PATH
    )

    if args.validate:
        run_validation_testset(optimized_extractor)
        return

    initial_text = """
4. Усильте беглость названия торговой марки, если вы хотите снизить уровень восприятия риска. Помните, что МакГлоун и Тофибакш утверждали, что чем легче обрабатывать информацию, тем более правдоподобной она становится. Люди путают легкость обработки информации и ее правдивость. Однако повышение беглости речи не только способствует повышению правдоподобности. По мнению Хенджина Сонга и Норберта Шварца из Мичиганского университета, она также может влиять на оценку риска. В 2009 году они показали участникам эксперимента список вымышленных пищевых добавок. Некоторые названия были труднопроизносимыми, например Hnegripitrom, а другие - легкопроизносимыми, например Magnalroxate. Затем психологи попросили испытуемых указать, насколько вредными, по их мнению, являются эти добавки, по семибалльной шкале: 1 означает, что препарат очень безопасен, а 7 - что он очень вреден. Добавки с труднопроизносимыми названиями получили среднюю оценку 4,12 балла, в то время как более легко произносимые слова - 3,70 балла. Это на 11% больше, чем в случае труднопроизносимых слов. Психологи утверждали, что легкость произношения отождествляется с риском. Этот вывод можно легко применить в рекламе - если вы хотите убедить своих клиентов в том, что ваш препарат или новая разработка не представляют особого риска, выберите легко произносимое название бренда. Однако бывают случаи, когда необходимо подчеркнуть, насколько интересным или рискованным является ваш продукт. В этом случае лучше дать продукту труднопроизносимое название. Психологи проверили эту идею на примере вымышленных аттракционов в парке развлечений. Они обнаружили, что аттракционы с труднопроизносимыми названиями считаются более рискованными, но и более захватывающими. Shotton Richard, The Illusion of Choice 16½ psychological biases that influence what we buy, 2023. // 5: The Keats Heuristic.
"""
    # Пример вызова с новыми параметрами и обработка результатов
    final_triplets, _, failed_details = process_text(optimized_extractor, initial_text, banal_threshold=0.6, reproducibility_threshold=0.7)

    print("\n--- Итоговые обработанные связки ---")
    if final_triplets:
        for i, triplet in enumerate(final_triplets, 1):
            print(f"Связка {i}:")
            print(f"  Начальное состояние: {triplet.get('initial_state', 'N/A')}")
            print(f"  Преобразование: {triplet.get('transformation', 'N/A')}")
            print(f"  Результат: {triplet.get('result', 'N/A')}")
    else:
        print("Не найдено связок, прошедших все фильтры.")

    if failed_details:
        print("\n--- Детали отфильтрованных связок ---")
        print(failed_details)

if __name__ == "__main__":
    main()