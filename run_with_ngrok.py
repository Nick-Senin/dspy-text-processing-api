#!/usr/bin/env python3
"""
Скрипт для запуска Flask сервера с ngrok туннелем.
Это позволяет получить публичный URL для доступа к API.
"""

import os
import sys
import threading
import time
from pyngrok import ngrok, conf

# Настройки ngrok
NGROK_AUTH_TOKEN = "2xlekxGLWrTgk1gGX4S5wAXtCQZ_2cH9Q17JfRavSnPvCL8G9"  # Ваш токен
PORT = 5000

def setup_ngrok():
    """Настраивает и запускает ngrok туннель."""
    try:
        # Устанавливаем токен аутентификации
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        
        # Создаем HTTP туннель
        print(f"🔗 Создание ngrok туннеля на порт {PORT}...")
        public_tunnel = ngrok.connect(PORT)
        public_url = public_tunnel.public_url
        
        print(f"✅ Ngrok туннель создан!")
        print(f"🌐 Публичный URL: {public_url}")
        print(f"📝 API эндпоинты:")
        print(f"   - {public_url}/health")
        print(f"   - {public_url}/process")
        print(f"   - {public_url}/")
        
        return public_url
        
    except Exception as e:
        print(f"❌ Ошибка при создании ngrok туннеля: {e}")
        print("Проверьте:")
        print("1. Установлен ли pyngrok: pip install pyngrok")
        print("2. Корректность токена ngrok")
        print("3. Интернет-соединение")
        return None

def run_flask_server():
    """Запускает Flask сервер."""
    try:
        # Проверяем, что мы в корневой папке проекта
        if not os.path.exists('server/app.py'):
            print("❌ Ошибка: Не найден файл server/app.py")
            print("Пожалуйста, запустите этот скрипт из корневой папки проекта.")
            return False
        
        # Добавляем папку server в путь Python
        server_path = os.path.join(os.getcwd(), 'server')
        if server_path not in sys.path:
            sys.path.insert(0, server_path)
        
        # Импортируем приложение
        from server.app import app
        
        print(f"🚀 Запуск Flask сервера на порту {PORT}...")
        
        # Запускаем сервер без debug режима для ngrok
        app.run(host='0.0.0.0', port=PORT, debug=False)
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Проверьте, что все зависимости установлены: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка при запуске сервера: {e}")
        return False

def main():
    """Основная функция."""
    print("🌐 Запуск Flask сервера с ngrok туннелем")
    print("="*60)
    
    # Создаем ngrok туннель
    public_url = setup_ngrok()
    if not public_url:
        print("❌ Не удалось создать ngrok туннель. Завершение работы.")
        return
    
    print("\n" + "="*60)
    
    try:
        # Запускаем Flask сервер
        print("⏹️  Для остановки нажмите Ctrl+C")
        print("\n📝 Пример тестового запроса:")
        print(f"curl {public_url}/health")
        print("\n" + "-"*60)
        
        run_flask_server()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка сервера...")
        
    finally:
        # Закрываем все ngrok туннели
        try:
            print("🔗 Закрытие ngrok туннелей...")
            ngrok.kill()
            print("✅ Ngrok туннели закрыты.")
        except:
            pass
        
        print("👋 До свидания!")

if __name__ == "__main__":
    main()