# run_simple_tests.py
#!/usr/bin/env python3
"""
Простой запуск тестов для Компьютерного салона
"""

import sys
import os

def main():
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ 'КОМПЬЮТЕРНЫЙ САЛОН'")
    print("=" * 60)
    
    # Добавляем текущую директорию в путь
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    total_success = True
    
    try:
        print("\n1. ТЕСТЫ БАЗОВЫХ ФУНКЦИЙ")
        print("-" * 40)
        from simple_tests import run_all_tests
        success1 = run_all_tests()
        total_success = total_success and success1
        
    except Exception as e:
        print(f"❌ Ошибка при запуске базовых тестов: {e}")
        total_success = False
    
    try:
        print("\n2. ТЕСТЫ БАЗЫ ДАННЫХ")
        print("-" * 40)
        from db_tests import run_database_tests
        success2 = run_database_tests()
        total_success = total_success and success2
        
    except Exception as e:
        print(f"❌ Ошибка при запуске тестов БД: {e}")
        total_success = False
    
    print("\n" + "=" * 60)
    if total_success:
        print("🎉 ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ!")
        print("✅ Система готова к работе")
    else:
        print("⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("🔧 Рекомендуется проверить систему")
    
    print("=" * 60)
    return 0 if total_success else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)