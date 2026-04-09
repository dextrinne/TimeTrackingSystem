"""
Конфигурация приложения.
"""

# Настройки подключения к PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'time_tracking',
    'user': 'postgres',
    'password': 'postgres'  # Измените на ваш пароль PostgreSQL
}

# Настройки приложения
APP_CONFIG = {
    'title': 'Учёт рабочего времени сотрудников ИММИ КубГУ',
    'version': '1.0.0',
    'organization': 'ИММИ КубГУ'
}

# Настройки экспорта
EXPORT_CONFIG = {
    'default_format': 'xlsx',
    'export_directory': 'exports'
}

# Единственная роль: Табельщик (полный доступ ко всем функциям системы)
ROLE_PERMISSIONS = {
    'Табельщик': {
        'employees': ['read', 'create', 'update', 'delete'],
        'timesheets': ['read', 'create', 'update', 'delete', 'approve', 'archive'],
        'documents': ['read', 'create', 'update', 'delete'],
        'reports': ['read', 'export'],
        'users': ['read'],
        'settings': ['read', 'update']
    }
}
