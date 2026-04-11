"""
Быстрый запуск ПС «Учёт рабочего времени сотрудников института» без компиляции.
"""

import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == '__main__':
    main()
