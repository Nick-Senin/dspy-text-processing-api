import requests
import json
import time

# URL сервера
BASE_URL = "http://localhost:5000"

def test_health():
    """Тестирует эндпоинт проверки здоровья."""
    print("\n🔍 Тестирование /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_index():
    """Тестирует главную страницу."""
    print("\n🏠 Тестирование /...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Статус: {response.status_code}")
        data = response.json()
        print(f"Сообщение: {data.get('message')}")
        print(f"Доступные эндпоинты: {list(data.get('endpoints', {}).keys())}")
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_process_simple():
    """Тестирует обработку простого текста."""
    print("\n📝 Тестирование /process с простым текстом...")
    
    data = {
        "text": "Человек решает проблему. Он применяет новый подход. Получается хороший результат.",
        "banal_threshold": 0.6,
        "reproducibility_threshold": 0.7
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/process",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Статус: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Успешно обработано")
            print(f"Отфильтрованных связок: {result.get('processed_count', 0)}")
            print(f"Всего связок: {result.get('total_count', 0)}")
            
            # Показываем первые несколько связок
            filtered = result.get('filtered_triplets', [])
            unfiltered = result.get('unfiltered_triplets', [])
            
            if filtered:
                print(f"\nПример отфильтрованной связки:")
                print(json.dumps(filtered[0], ensure_ascii=False, indent=2))
            
            if unfiltered:
                print(f"\nПример необработанной связки:")
                print(json.dumps(unfiltered[0], ensure_ascii=False, indent=2))
                
            if result.get('failed_reasoning'):
                print(f"\nПричины отфильтровки (первые 200 символов):")
                print(result['failed_reasoning'][:200] + "...")
        else:
            print(f"❌ Ошибка: {result.get('message')}")
            
        return response.status_code == 200 and result.get('success')
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_process_complex():
    """Тестирует обработку более сложного текста."""
    print("\n📚 Тестирование /process со сложным текстом...")
    
    data = {
        "text": """Когда человек сталкивается с проблемой, он часто пытается решить её привычными способами. 
        Однако иногда требуется изменить подход к решению проблемы. 
        Применение нового метода может привести к неожиданному и эффективному результату. 
        Важно не бояться экспериментировать и пробовать различные варианты решения.""",
        "banal_threshold": 0.5,
        "reproducibility_threshold": 0.6
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/process",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=60  # Увеличиваем timeout для сложного текста
        )
        end_time = time.time()
        
        print(f"Статус: {response.status_code}")
        print(f"Время обработки: {end_time - start_time:.2f} секунд")
        
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Успешно обработано")
            print(f"Отфильтрованных связок: {result.get('processed_count', 0)}")
            print(f"Всего связок: {result.get('total_count', 0)}")
            
            # Показываем статистику
            filtered_count = len(result.get('filtered_triplets', []))
            total_count = len(result.get('unfiltered_triplets', []))
            filter_rate = (total_count - filtered_count) / total_count * 100 if total_count > 0 else 0
            
            print(f"Процент отфильтрованных: {filter_rate:.1f}%")
            
        else:
            print(f"❌ Ошибка: {result.get('message')}")
            
        return response.status_code == 200 and result.get('success')
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_error_cases():
    """Тестирует обработку ошибочных случаев."""
    print("\n⚠️ Тестирование обработки ошибок...")
    
    # Тест 1: Пустой запрос
    try:
        response = requests.post(f"{BASE_URL}/process", json={})
        print(f"Пустой запрос - Статус: {response.status_code}")
        result = response.json()
        print(f"Сообщение: {result.get('message')}")
    except Exception as e:
        print(f"Ошибка при тесте пустого запроса: {e}")
    
    # Тест 2: Отсутствует поле text
    try:
        response = requests.post(f"{BASE_URL}/process", json={"banal_threshold": 0.5})
        print(f"Без поля text - Статус: {response.status_code}")
        result = response.json()
        print(f"Сообщение: {result.get('message')}")
    except Exception as e:
        print(f"Ошибка при тесте без text: {e}")
    
    # Тест 3: Неверный тип данных для порогов
    try:
        response = requests.post(f"{BASE_URL}/process", json={
            "text": "Тест",
            "banal_threshold": "не число"
        })
        print(f"Неверный тип данных - Статус: {response.status_code}")
        result = response.json()
        print(f"Сообщение: {result.get('message')}")
    except Exception as e:
        print(f"Ошибка при тесте неверного типа: {e}")
    
    return True

def main():
    """Запускает все тесты."""
    print("🚀 Запуск тестов Flask сервера...")
    print(f"Базовый URL: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health),
        ("Index Page", test_index),
        ("Simple Processing", test_process_simple),
        ("Complex Processing", test_process_complex),
        ("Error Cases", test_error_cases)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Тест: {test_name}")
        print(f"{'='*50}")
        
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"\n{'✅ ПРОЙДЕН' if success else '❌ НЕ ПРОЙДЕН'}")
        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print(f"\n\n{'='*60}")
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ ПРОЙДЕН" if success else "❌ НЕ ПРОЙДЕН"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nВсего тестов: {total}")
    print(f"Пройдено: {passed}")
    print(f"Не пройдено: {total - passed}")
    print(f"Успешность: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Все тесты пройдены успешно!")
    else:
        print("\n⚠️ Некоторые тесты не пройдены. Проверьте логи выше.")

if __name__ == "__main__":
    main()