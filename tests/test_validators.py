"""
Модульные тесты валидаторов (ЛР1: календарный план — тестирование).
"""

import unittest
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.validators import Validator


class TestEmployeeValidation(unittest.TestCase):
    """Тесты валидации сотрудников."""

    def test_valid_employee(self):
        """Корректные данные сотрудника."""
        is_valid, error = Validator.validate_employee_data(
            'Иванов Иван Иванович', 'Научный сотрудник', 1.0, 40
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_empty_fio(self):
        """Пустое ФИО."""
        is_valid, error = Validator.validate_employee_data(
            '', 'Сотрудник', 1.0, 40
        )
        self.assertFalse(is_valid)
        self.assertIn('ФИО', error)

    def test_negative_rate(self):
        """Отрицательная ставка."""
        is_valid, error = Validator.validate_employee_data(
            'Петров П.П.', 'Сотрудник', -0.5, 40
        )
        self.assertFalse(is_valid)
        self.assertIn('ставка', error.lower())

    def test_negative_norm_hours(self):
        """Отрицательные часы нормы."""
        is_valid, error = Validator.validate_employee_data(
            'Петров П.П.', 'Сотрудник', 1.0, -10
        )
        self.assertFalse(is_valid)
        self.assertIn('отрицательной', error)


class TestDocumentValidation(unittest.TestCase):
    """Тесты валидации документов."""

    def test_valid_document_dates(self):
        """Корректные даты документа."""
        is_valid, error = Validator.validate_dates(
            date(2026, 3, 1), date(2026, 3, 14)
        )
        self.assertTrue(is_valid)

    def test_end_before_start(self):
        """Дата окончания раньше даты начала."""
        is_valid, error = Validator.validate_dates(
            date(2026, 3, 14), date(2026, 3, 1)
        )
        self.assertFalse(is_valid)
        self.assertIn('окончания', error.lower())

    def test_valid_document_type(self):
        """Корректный тип документа."""
        is_valid, error = Validator.validate_document_type('Отпуск')
        self.assertTrue(is_valid)

    def test_invalid_document_type(self):
        """Недопустимый тип документа."""
        is_valid, error = Validator.validate_document_type('Неизвестный')
        self.assertFalse(is_valid)


class TestTimesheetValidation(unittest.TestCase):
    """Тесты валидации табелей."""

    def test_valid_timesheet_dates(self):
        """Корректные даты табеля."""
        is_valid, error = Validator.validate_dates(
            date(2026, 3, 1), date(2026, 3, 31)
        )
        self.assertTrue(is_valid)

    def test_valid_status(self):
        """Корректный статус табеля."""
        is_valid, error = Validator.validate_timesheet_status('В работе')
        self.assertTrue(is_valid)

    def test_invalid_status(self):
        """Недопустимый статус табеля."""
        is_valid, error = Validator.validate_timesheet_status('Неизвестный')
        self.assertFalse(is_valid)


class TestHoursValidation(unittest.TestCase):
    """Тесты валидации часов."""

    def test_valid_hours(self):
        """Корректные часы."""
        is_valid, error = Validator.validate_hours(8.0)
        self.assertTrue(is_valid)

    def test_negative_hours(self):
        """Отрицательные часы."""
        is_valid, error = Validator.validate_hours(-5.0)
        self.assertFalse(is_valid)

    def test_hours_over_24(self):
        """Часы больше 24."""
        is_valid, error = Validator.validate_hours(30.0)
        self.assertFalse(is_valid)


class TestDayTypeValidation(unittest.TestCase):
    """Тесты валидации типов дней."""

    def test_valid_day_types(self):
        """Корректные типы дней."""
        for day_type in ['Рабочий день', 'Отпуск', 'Больничный', 'Командировка', 'Отгул', 'Неявка']:
            is_valid, error = Validator.validate_day_type(day_type)
            self.assertTrue(is_valid, f"Тип '{day_type}' должен быть валидным")

    def test_invalid_day_type(self):
        """Недопустимый тип дня."""
        is_valid, error = Validator.validate_day_type('Неизвестный')
        self.assertFalse(is_valid)


class TestLoginValidation(unittest.TestCase):
    """Тесты валидации авторизации."""

    def test_valid_credentials(self):
        """Корректные данные для входа."""
        is_valid, error = Validator.validate_login_credentials('tabel', 'tabel123')
        self.assertTrue(is_valid)

    def test_empty_username(self):
        """Пустой логин."""
        is_valid, error = Validator.validate_login_credentials('', 'password')
        self.assertFalse(is_valid)

    def test_empty_password(self):
        """Пустой пароль."""
        is_valid, error = Validator.validate_login_credentials('user', '')
        self.assertFalse(is_valid)


if __name__ == '__main__':
    unittest.main()
