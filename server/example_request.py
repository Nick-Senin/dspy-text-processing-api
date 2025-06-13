import requests
import json

# Конфигурация
SERVER_URL = "http://localhost:5000"  # Локальный сервер
# SERVER_URL = "https://081d-138-68-156-65.ngrok-free.app"  # Ngrok URL

def make_request(text, banal_threshold=0.6, reproducibility_threshold=0.7):
    """Отправляет запрос на обработку текста."""
    
    data = {
        "text": text,
        "banal_threshold": banal_threshold,
        "reproducibility_threshold": reproducibility_threshold
    }
    
    try:
        print(f"🚀 Отправка запроса на {SERVER_URL}/process")
        print(f"📝 Текст: {text[:100]}{'...' if len(text) > 100 else ''}")
        print(f"🎯 Пороги: банальность={banal_threshold}, воспроизводимость={reproducibility_threshold}")
        print("\n" + "="*60)
        
        response = requests.post(
            f"{SERVER_URL}/process",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ Обработка завершена успешно!\n")
                
                # Основная статистика
                filtered_count = result.get('processed_count', 0)
                total_count = result.get('total_count', 0)
                filter_rate = (total_count - filtered_count) / total_count * 100 if total_count > 0 else 0
                
                print(f"📈 СТАТИСТИКА:")
                print(f"   Всего извлечено связок: {total_count}")
                print(f"   Прошло фильтры: {filtered_count}")
                print(f"   Отфильтровано: {total_count - filtered_count} ({filter_rate:.1f}%)")
                
                # Отфильтрованные связки
                filtered_triplets = result.get('filtered_triplets', [])
                if filtered_triplets:
                    print(f"\n🎯 ОТФИЛЬТРОВАННЫЕ СВЯЗКИ ({len(filtered_triplets)}):")
                    for i, triplet in enumerate(filtered_triplets, 1):
                        print(f"\n   {i}. Исходное состояние: {triplet.get('initial_state', 'N/A')}")
                        print(f"      Трансформация: {triplet.get('transformation', 'N/A')}")
                        print(f"      Результат: {triplet.get('result', 'N/A')}")
                else:
                    print("\n🎯 ОТФИЛЬТРОВАННЫЕ СВЯЗКИ: Нет")
                
                # Все извлеченные связки
                unfiltered_triplets = result.get('unfiltered_triplets', [])
                if unfiltered_triplets:
                    print(f"\n📋 ВСЕ ИЗВЛЕЧЕННЫЕ СВЯЗКИ ({len(unfiltered_triplets)}):")
                    for i, triplet in enumerate(unfiltered_triplets, 1):
                        print(f"\n   {i}. Исходное состояние: {triplet.get('initial_state', 'N/A')}")
                        print(f"      Трансформация: {triplet.get('transformation', 'N/A')}")
                        print(f"      Результат: {triplet.get('result', 'N/A')}")
                
                # Причины отфильтровки
                failed_reasoning = result.get('failed_reasoning', '')
                if failed_reasoning:
                    print(f"\n❌ ПРИЧИНЫ ОТФИЛЬТРОВКИ:")
                    print(f"   {failed_reasoning}")
                else:
                    print(f"\n❌ ПРИЧИНЫ ОТФИЛЬТРОВКИ: Нет отфильтрованных связок")
                    
            else:
                print(f"❌ Ошибка обработки: {result.get('message')}")
                
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Сообщение: {error_data.get('message', 'Неизвестная ошибка')}")
            except:
                print(f"   Текст ответа: {response.text}")
                
    except requests.exceptions.Timeout:
        print("⏰ Превышено время ожидания ответа")
    except requests.exceptions.ConnectionError:
        print("🔌 Ошибка подключения к серверу")
    except Exception as e:
        print(f"💥 Неожиданная ошибка: {e}")

def main():
    """Демонстрирует различные примеры использования API."""
    
    print("🎯 Демонстрация API для обработки текста")
    print("="*60)
    
    # Пример 1: Простой текст
    print("\n🔹 ПРИМЕР 1: Простой текст")
    simple_text = "Человек решает проблему. Он применяет новый подход. Получается хороший результат."
    make_request(simple_text, banal_threshold=0.6, reproducibility_threshold=0.7)
    
    # Пример 2: Более сложный текст
    print("\n\n🔹 ПРИМЕР 2: Сложный текст")
    complex_text = """Когда человек сталкивается с проблемой, он часто пытается решить её привычными способами. 
    Однако иногда требуется изменить подход к решению проблемы. 
    Применение нового метода может привести к неожиданному и эффективному результату. 
    Важно не бояться экспериментировать и пробовать различные варианты решения."""
    make_request(complex_text, banal_threshold=0.5, reproducibility_threshold=0.6)
    
    # Пример 3: Текст с более строгими фильтрами
    print("\n\n🔹 ПРИМЕР 3: Строгие фильтры")
    make_request(simple_text, banal_threshold=0.8, reproducibility_threshold=0.9)
    
    print("\n" + "="*60)
    print("✨ Демонстрация завершена!")

if __name__ == "__main__":
    main()