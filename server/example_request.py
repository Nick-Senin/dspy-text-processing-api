#!/usr/bin/env python3
"""
Пример запроса к Flask серверу для обработки текста.
"""

import requests
import json

def main():
    # URL сервера
    url = "http://localhost:5000/process"
    
    # Пример текста для обработки
    sample_text = """
    Когда человек сталкивается с проблемой, он часто пытается решить её привычными способами. 
    Однако иногда требуется изменить подход к решению проблемы. 
    Применение нового метода может привести к неожиданному и эффективному результату.
    """
    
    # Данные для отправки
    data = {
        "text": sample_text.strip(),
        "banal_threshold": 0.6,
        "reproducibility_threshold": 0.7
    }
    
    print("🚀 Отправка запроса к Flask серверу...")
    print(f"📝 Текст: {data['text'][:100]}...")
    print(f"🎯 Порог банальности: {data['banal_threshold']}")
    print(f"🔄 Порог воспроизводимости: {data['reproducibility_threshold']}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(
            url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        # Проверяем статус ответа
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ Запрос выполнен успешно!")
            print(f"📊 Всего извлечено связок: {result.get('total_count', 0)}")
            print(f"✨ Прошло фильтры: {result.get('processed_count', 0)}")
            
            # Показываем отфильтрованные связки (прошедшие все фильтры)
            filtered = result.get('filtered_triplets', [])
            if filtered:
                print(f"\n✅ Отфильтрованные связки (прошли все фильтры) ({len(filtered)}):")
                for i, triplet in enumerate(filtered, 1):
                    print(f"\n  {i}. Связка:")
                    print(f"     Начальное состояние: {triplet.get('initial_state', 'N/A')}")
                    print(f"     Преобразование: {triplet.get('transformation', 'N/A')}")
                    print(f"     Результат: {triplet.get('result', 'N/A')}")
            
            # Показываем неотфильтрованные связки
            unfiltered = result.get('unfiltered_triplets', [])
            if unfiltered:
                print(f"\n📋 Все извлеченные связки ({len(unfiltered)}):")
                for i, triplet in enumerate(unfiltered, 1):
                    print(f"\n  {i}. Связка:")
                    print(f"     Начальное состояние: {triplet.get('initial_state', 'N/A')}")
                    print(f"     Преобразование: {triplet.get('transformation', 'N/A')}")
                    print(f"     Результат: {triplet.get('result', 'N/A')}")
            
            # Показываем рассуждения об отфильтрованных
            failed_reasoning = result.get('failed_reasoning', '')
            if failed_reasoning:
                print(f"\n🚫 Рассуждения об отфильтрованных связках:")
                print(failed_reasoning)
            
        else:
            print(f"\n❌ Ошибка HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Сообщение: {error_data.get('message', 'Неизвестная ошибка')}")
            except:
                print(f"Ответ сервера: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("\n❌ Не удалось подключиться к серверу.")
        print("Убедитесь, что Flask сервер запущен: python app.py")
        
    except requests.exceptions.Timeout:
        print("\n⏰ Превышено время ожидания ответа от сервера.")
        
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")

if __name__ == "__main__":
    main()