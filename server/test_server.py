import requests
import json

# Тестовые данные
test_data = {
    "text": "Пример текста для тестирования. Это простой текст, который должен быть обработан системой извлечения преобразований.",
    "banal_threshold": 0.6,
    "reproducibility_threshold": 0.7
}

def test_server():
    """Тестирует работу Flask сервера."""
    base_url = "http://localhost:5000"
    
    print("🔍 Тестирование Flask сервера...")
    
    # Тест 1: Проверка состояния сервера
    print("\n1. Проверка состояния сервера...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Сервер не запущен. Запустите сервер командой: python app.py")
        return
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return
    
    # Тест 2: Главная страница
    print("\n2. Проверка главной страницы...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 3: Обработка текста
    print("\n3. Тестирование обработки текста...")
    try:
        response = requests.post(
            f"{base_url}/process",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Статус: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print("   ✅ Обработка успешна!")
            print(f"   📊 Всего связок: {result.get('total_count', 0)}")
            print(f"   ✨ Прошло фильтры: {result.get('processed_count', 0)}")
            
            if result.get('filtered_triplets'):
                print(f"   ✅ Первая отфильтрованная связка: {result['filtered_triplets'][0]}")
            
            if result.get('unfiltered_triplets'):
                print(f"   📝 Первая неотфильтрованная связка: {result['unfiltered_triplets'][0]}")
            
            if result.get('failed_reasoning'):
                print(f"   🚫 Детали отфильтрованных: {result['failed_reasoning'][:200]}...")
        else:
            print(f"   ❌ Ошибка обработки: {result.get('message')}")
            
    except Exception as e:
        print(f"   ❌ Ошибка запроса: {e}")
    
    # Тест 4: Обработка с неправильными данными
    print("\n4. Тестирование обработки ошибок...")
    try:
        response = requests.post(
            f"{base_url}/process",
            json={"invalid": "data"},
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Статус: {response.status_code}")
        result = response.json()
        print(f"   Ответ: {result.get('message')}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_server()