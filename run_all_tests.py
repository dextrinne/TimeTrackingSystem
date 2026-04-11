"""
Главный файл запуска всех тестов ПС «Учёт рабочего времени».

Запуск:
    python run_all_tests.py
    
Запуск с подробным выводом:
    python run_all_tests.py -v

Запуск конкретного модуля:
    python -m unittest tests.test_models_comprehensive
"""

import unittest
import sys
import os
import time

# Добавляем корень проекта в path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def load_all_tests():
    """Загрузка всех тестов."""
    # Создаем загрузчик
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Список всех тестовых модулей
    test_modules = [
        'tests.test_models',
        'tests.test_models_comprehensive',
        'tests.test_services',
        'tests.test_services_comprehensive',
        'tests.test_validators',
        'tests.test_validators_comprehensive',
        'tests.test_db_manager',
        'tests.test_login_dialog',
        'tests.test_dialogs',
        'tests.test_tabs',
        'tests.test_main_window',
        'tests.test_integration',
        'tests.test_errors_and_edge_cases',
    ]
    
    # Загружаем каждый модуль
    for module_name in test_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            tests = loader.loadTestsFromModule(module)
            suite.addTest(tests)
            print(f'✓ Загружен: {module_name}')
        except Exception as e:
            print(f'✗ Ошибка загрузки {module_name}: {e}')
    
    return suite


def run_tests(verbosity=2):
    """Запуск всех тестов."""
    print('=' * 70)
    print('ЗАПУСК ВСЕХ ТЕСТОВ ПС «УЧЁТ РАБОЧЕГО ВРЕМЕНИ»')
    print('=' * 70)
    print()
    
    start_time = time.time()
    
    # Загружаем все тесты
    suite = load_all_tests()
    
    print()
    print('-' * 70)
    print('ВЫПОЛНЕНИЕ ТЕСТОВ:')
    print('-' * 70)
    print()
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Выводим итоговую статистику
    print()
    print('=' * 70)
    print('ИТОГОВАЯ СТАТИСТИКА:')
    print('=' * 70)
    print(f'Всего тестов выполнено: {result.testsRun}')
    print(f'Успешно: {result.testsRun - len(result.failures) - len(result.errors)}')
    print(f'Ошибок: {len(result.errors)}')
    print(f'Неуспешных: {len(result.failures)}')
    print(f'Пропущено: {len(result.skipped)}')
    print(f'Время выполнения: {duration:.2f} сек')
    print('=' * 70)
    
    if result.wasSuccessful():
        print()
        print('✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!')
        print()
    else:
        print()
        print('❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ')
        print()
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Определяем уровень verbosity из аргументов
    verbosity = 2
    if '-v' in sys.argv:
        verbosity = 2
    elif '-q' in sys.argv:
        verbosity = 0
    
    exit_code = run_tests(verbosity)
    sys.exit(exit_code)
