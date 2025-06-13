#!/usr/bin/env python3
"""
Скрипт для запуска Flask сервера из корневой папки проекта.
"""

import os
import sys
import subprocess

def main():
    # Получаем путь к корневой папке проекта
    project_root = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(project_root, 'server', 'app.py')
    
    print("🚀 Запуск Flask сервера...")
    print(f"📁 Корневая папка проекта: {project_root}")
    print(f"🌐 Сервер будет доступен по адресу: http://localhost:5000")
    print("📖 Документация: server/README_FLASK.md")
    print("🧪 Тестирование: cd server && python test_server.py")
    print("-" * 50)
    
    try:
        # Запускаем сервер
        subprocess.run([sys.executable, server_path], cwd=project_root)
    except KeyboardInterrupt:
        print("\n⏹️  Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка при запуске сервера: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())