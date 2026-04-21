import os
from pathlib import Path


class AppConfig:
    """Основные настройки приложения"""
    
    # Пути
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    ARCHIVE_DIR = BASE_DIR / 'archive'
    TEMPLATES_DIR = BASE_DIR / 'templates'
    
    # Файлы данных
    EMPLOYEES_FILE = DATA_DIR / 'employees.json'
    
    # Основные настройки окна
    APP_TITLE = "Табель учета рабочего времени"
    WINDOW_SIZE = "1600x900"
    
    # Настройки по умолчанию
    DEFAULT_YEAR = 2026
    DEFAULT_MONTH = 1  # январь
    
    # Список месяцев
    MONTHS = [
        'январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
        'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'
    ]
    
    # Настройки отмены действий
    MAX_UNDO_DEPTH = 50
    
    # Настройки автосохранения
    AUTOSAVE_DELAY = 2000  # миллисекунды
    AUTOSAVE_ENABLED = True
    
    # Настройки экспорта
    EXPORT_FILE_TYPES = [("Excel files", "*.xls"), ("All files", "*.*")]
    
    # Настройки валидации
    MIN_RATE = 0.0
    MAX_RATE = 1.0
    DEFAULT_RATE = 1.0
    
    @classmethod
    def ensure_directories(cls):
        """Создать необходимые директории"""
        directories = [cls.DATA_DIR, cls.ARCHIVE_DIR, cls.TEMPLATES_DIR]
        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)

class UIConfig:
    """Настройки пользовательского интерфейса"""
    
    # Размеры ячеек календаря
    CELL_WIDTH = 4
    CELL_HEIGHT = 2
    
    # Настройки отображения кодов
    SHOW_FULL_CODES = False  # Показывать полные коды (ОТ) или короткие (О)
    MAX_CODE_LENGTH = 3      # Максимальная длина кода на кнопке
    
    # Настройки тултипов
    TOOLTIP_DELAY = 500      # Задержка перед показом (мс)
    TOOLTIP_BG = '#FFFFE0'   # Цвет фона тултипа
    
    # Группы для отображения в информационной панели
    INFO_PANEL_TYPES = ['Р', 'В', 'ОТ', 'Б', 'К']