#!/usr/bin/env python3
"""
Скрипт для запуска Flask сервера из корневой папки проекта.
Это удобно, чтобы не переходить в папку server.
"""

import os
import sys

def main():
    """Запускает Flask сервер."""
    
    # Проверяем, что мы в корневой папке проекта
    if not os.path.exists('server/app.py'):
        print("❌ Ошибка: Не найден файл server/app.py")
        print("Пожалуйста, запустите этот скрипт из корневой папки проекта.")
        sys.exit(1)
    
    print("🚀 Запуск Flask сервера...")
    print("📁 Путь к серверу: server/app.py")
    print("🌐 Сервер будет доступен по адресу: http://localhost:5000")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("\n" + "="*60)
    
    # Добавляем папку server в путь Python
    server_path = os.path.join(os.getcwd(), 'server')
    if server_path not in sys.path:
        sys.path.insert(0, server_path)
    
    try:
        # Импортируем и запускаем приложение
        from server.app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Проверьте, что все зависимости установлены: pip install -r requirements.txt")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Сервер остановлен пользователем.")
        
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()