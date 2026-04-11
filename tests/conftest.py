"""
Фикстуры и общая инфраструктура для тестов.
Использует только psycopg2 моки (без SQLite).
"""

import sys
import os
import pytest
from datetime import date, datetime
from unittest.mock import Mock

# Добавляем корень проекта в path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope='session')
def project_root():
    """Корневая директория проекта."""
    return os.path.join(os.path.dirname(__file__), '..')


@pytest.fixture
def mock_db():
    """Создание мока DatabaseManager."""
    return Mock()


@pytest.fixture
def sample_employee_data():
    """Пример данных сотрудника."""
    return {
        'fio': 'Иванов Иван Иванович',
        'position': 'Научный сотрудник',
        'rate': 1.0,
        'norm_hours': 40
    }


@pytest.fixture
def sample_timesheet_data():
    """Пример данных табеля."""
    return {
        'period_start': date(2026, 3, 1),
        'period_end': date(2026, 3, 31),
        'status': 'В работе'
    }


@pytest.fixture
def sample_document_data():
    """Пример данных документа."""
    return {
        'employee_id': 1,
        'type': 'Отпуск',
        'start_date': date(2026, 3, 1),
        'end_date': date(2026, 3, 14)
    }


@pytest.fixture
def sample_user_data():
    """Пример данных пользователя."""
    import hashlib
    password = 'testpass123'
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    return {
        'username': 'testuser',
        'password_hash': password_hash,
        'role': 'Табельщик',
        'employee_id': None
    }


@pytest.fixture
def sample_timesheet_entry_data():
    """Пример данных записи табеля."""
    return {
        'employee_id': 1,
        'timesheet_id': 1,
        'date': date(2026, 3, 2),
        'hours_worked': 8.0,
        'type': 'Рабочий день'
    }


@pytest.fixture
def mock_db_with_employees(mock_db):
    """Мок БД с данными сотрудников."""
    mock_db.execute_query.return_value = [
        (1, 'Иванов И.И.', 'Инженер', 1.0, 40),
        (2, 'Петров П.П.', 'Научный сотрудник', 0.5, 20),
    ]
    return mock_db


@pytest.fixture
def mock_db_with_timesheets(mock_db):
    """Мок БД с данными табелей."""
    from datetime import datetime
    mock_db.execute_query.return_value = [
        (1, date(2026, 3, 1), date(2026, 3, 31), 'В работе', datetime.now(), None, None),
    ]
    return mock_db
