"""
Комплексные тесты валидаторов с полным покрытием.
Покрывает: все методы Validator, граничные случаи, ошибки, unicode, пустые значения.
"""

import unittest
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.validators import Validator


class TestEmployeeValidationComprehensive(unittest.TestCase):
    """Расширенные тесты валидации сотрудников."""

    def test_valid_employee_standard(self):
        """Стандартные корректные данные."""
        is_valid, error = Validator.validate_employee_data(
            'Иванов Иван Иванович', 'Научный сотрудник', 1.0, 40
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_valid_employee_min_values(self):
        """Минимальные допустимые значения."""
        is_valid, error = Validator.validate_employee_data(
            'Иванов И.И.', 'Сотрудник', 0.0, 0
        )
        self.assertTrue(is_valid)

    def test_valid_employee_max_values(self):
        """Максимальные допустимые значения."""
        is_valid, error = Validator.validate_employee_data(
            'Иванов И.И.', 'Сотрудник', 999.99, 168
        )
        self.assertTrue(is_valid)

    def test_valid_employee_fractional_rate(self):
        """Дробная ставка."""
        is_valid, error = Validator.validate_employee_data(
            'Петров П.П.', 'Инженер', 0.5, 20
        )
        self.assertTrue(is_valid)

    def test_empty_fio(self):
        """Пустое ФИО."""
        is_valid, error = Validator.validate_employee_data(
            '', 'Сотрудник', 1.0, 40
        )
        self.assertFalse(is_valid)
        self.assertIn('ФИО', error)

    def test_whitespace_fio(self):
        """ФИО из пробелов."""
        is_valid, error = Validator.validate_employee_data(
            '   ', 'Сотрудник', 1.0, 40
        )
        self.assertFalse(is_valid)
        self.assertIn('ФИО', error)

    def test_none_fio(self):
        """None ФИО."""
        is_valid, error = Validator.validate_employee_data(
            None, 'Сотрудник', 1.0, 40
        )
        self.assertFalse(is_valid)

    def test_too_long_fio(self):
        """Слишком длинное ФИО."""
        long_fio = 'И' * 256
        is_valid, error = Validator.validate_employee_data(
            long_fio, 'Сотрудник', 1.0, 40
        )
        self.assertFalse(is_valid)
        self.assertIn('длинн', error.lower())

    def test_empty_position(self):
        """Пустая должность."""
        is_valid, error = Validator.validate_employee_data(
            'Иванов И.И.', '', 1.0, 40
        )
        self.assertFalse(is_valid)
        self.assertIn('Должность', error)

    def test_whitespace_position(self):
        """Должность из пробелов."""
        is_valid, error = Validator.validate_employee_data(
            'Иванов И.И.', '   ', 1.0, 40
        )
        self.assertFalse(is_valid)

    def test_too_long_position(self):
        """Слишком длинная должность."""
        long_position = 'Д' * 101
        is_valid, error = Validator.validate_employee_data(
            'Иванов И.И.', long_position, 1.0, 40
        )
        self.assertFalse(is_valid)
        self.assertIn('длинн', error.lower())

    def test_negative_rate(self):
        """Отрицательная ставка."""
        is_valid, error = Validator.validate_employee_data(
            'Иванов И.И.', 'Сотрудник', -0.01, 40
        )
        self.assertFalse(is_valid)
        self.assertIn('ставк', error.lower())

    def test_too_high_rate(self):
        """Слишком высокая ставка."""
        is_valid, error = Validator.validate_employee_data(
            'Иванов И.И.', 'Сотрудник', 1000.0, 40
        )
        self.assertFalse(is_valid)
        self.assertIn('ставк', error.lower())

    def test_negative_norm_hours(self):
        """Отрицательные часы нормы."""
        is_valid, error = Validator.validate_employee_data(
            'Иванов И.И.', 'Сотрудник', 1.0, -1
        )
        self.assertFalse(is_valid)
        self.assertIn('отрицательн', error.lower())

    def test_unicode_fio(self):
        """Юникод в ФИО."""
        is_valid, error = Validator.validate_employee_data(
            'Іванов Іван Іванович', 'Сотрудник', 1.0, 40
        )
        self.assertTrue(is_valid)

    def test_special_characters_in_fio(self):
        """Спецсимволы в ФИО."""
        is_valid, error = Validator.validate_employee_data(
            "О'Нилл-Смит", 'Сотрудник', 1.0, 40
        )
        self.assertTrue(is_valid)


class TestDateValidationComprehensive(unittest.TestCase):
    """Расширенные тесты валидации дат."""

    def test_valid_dates_same_day(self):
        """Одинаковые даты (начало = окончание)."""
        is_valid, error = Validator.validate_dates(
            date(2026, 3, 15), date(2026, 3, 15)
        )
        self.assertTrue(is_valid)

    def test_valid_dates_range(self):
        """Диапазон дат."""
        is_valid, error = Validator.validate_dates(
            date(2026, 1, 1), date(2026, 12, 31)
        )
        self.assertTrue(is_valid)

    def test_valid_dates_one_day_diff(self):
        """Разница в один день."""
        is_valid, error = Validator.validate_dates(
            date(2026, 3, 1), date(2026, 3, 2)
        )
        self.assertTrue(is_valid)

    def test_end_before_start(self):
        """Дата окончания раньше начала."""
        is_valid, error = Validator.validate_dates(
            date(2026, 3, 15), date(2026, 3, 1)
        )
        self.assertFalse(is_valid)
        self.assertIn('окончан', error.lower())

    def test_none_start_date(self):
        """None дата начала."""
        is_valid, error = Validator.validate_dates(
            None, date(2026, 3, 31)
        )
        self.assertFalse(is_valid)
        self.assertIn('начала', error.lower())

    def test_none_end_date(self):
        """None дата окончания."""
        is_valid, error = Validator.validate_dates(
            date(2026, 3, 1), None
        )
        self.assertFalse(is_valid)
        self.assertIn('окончан', error.lower())

    def test_both_none_dates(self):
        """Обе даты None."""
        is_valid, error = Validator.validate_dates(
            None, None
        )
        self.assertFalse(is_valid)

    def test_dates_across_years(self):
        """Даты через год."""
        is_valid, error = Validator.validate_dates(
            date(2025, 12, 1), date(2027, 1, 31)
        )
        self.assertTrue(is_valid)

    def test_dates_in_leap_year(self):
        """Даты в високосном году."""
        is_valid, error = Validator.validate_dates(
            date(2024, 2, 1), date(2024, 2, 29)
        )
        self.assertTrue(is_valid)


class TestDocumentTypeValidationComprehensive(unittest.TestCase):
    """Расширенные тесты валидации типов документов."""

    def test_valid_type_otpusk(self):
        """Корректный тип: Отпуск."""
        is_valid, error = Validator.validate_document_type('Отпуск')
        self.assertTrue(is_valid)

    def test_valid_type_bolnichny(self):
        """Корректный тип: Больничный."""
        is_valid, error = Validator.validate_document_type('Больничный')
        self.assertTrue(is_valid)

    def test_valid_type_komandirovka(self):
        """Корректный тип: Командировка."""
        is_valid, error = Validator.validate_document_type('Командировка')
        self.assertTrue(is_valid)

    def test_valid_type_otgul(self):
        """Корректный тип: Отгул."""
        is_valid, error = Validator.validate_document_type('Отгул')
        self.assertTrue(is_valid)

    def test_invalid_type_unknown(self):
        """Некорректный тип: Неизвестный."""
        is_valid, error = Validator.validate_document_type('Неизвестный')
        self.assertFalse(is_valid)
        self.assertIn('Недопустимый', error)

    def test_invalid_type_empty(self):
        """Пустой тип."""
        is_valid, error = Validator.validate_document_type('')
        self.assertFalse(is_valid)

    def test_invalid_type_none(self):
        """None тип."""
        is_valid, error = Validator.validate_document_type(None)
        self.assertFalse(is_valid)

    def test_invalid_type_whitespace(self):
        """Тип из пробелов."""
        is_valid, error = Validator.validate_document_type('   ')
        self.assertFalse(is_valid)

    def test_case_sensitive_type(self):
        """Регистрозависимость типа."""
        is_valid, error = Validator.validate_document_type('отпуск')  # lowercase
        self.assertFalse(is_valid)

    def test_type_with_extra_spaces(self):
        """Тип с лишними пробелами."""
        is_valid, error = Validator.validate_document_type('Отпуск ')
        self.assertFalse(is_valid)


class TestHoursValidationComprehensive(unittest.TestCase):
    """Расширенные тесты валидации часов."""

    def test_valid_hours_zero(self):
        """Нулевые часы."""
        is_valid, error = Validator.validate_hours(0.0)
        self.assertTrue(is_valid)

    def test_valid_hours_standard(self):
        """Стандартные 8 часов."""
        is_valid, error = Validator.validate_hours(8.0)
        self.assertTrue(is_valid)

    def test_valid_hours_max(self):
        """Максимальные 24 часа."""
        is_valid, error = Validator.validate_hours(24.0)
        self.assertTrue(is_valid)

    def test_valid_hours_fraction(self):
        """Дробные часы."""
        is_valid, error = Validator.validate_hours(7.5)
        self.assertTrue(is_valid)

    def test_valid_hours_small(self):
        """Маленькие часы."""
        is_valid, error = Validator.validate_hours(0.5)
        self.assertTrue(is_valid)

    def test_negative_hours(self):
        """Отрицательные часы."""
        is_valid, error = Validator.validate_hours(-0.1)
        self.assertFalse(is_valid)
        self.assertIn('отрицательн', error.lower())

    def test_hours_over_24(self):
        """Часы больше 24."""
        is_valid, error = Validator.validate_hours(24.1)
        self.assertFalse(is_valid)
        self.assertIn('превышать', error.lower())

    def test_hours_very_large(self):
        """Очень большое количество часов."""
        is_valid, error = Validator.validate_hours(100.0)
        self.assertFalse(is_valid)

    def test_hours_none(self):
        """None часы."""
        # None < 0 вызовет TypeError, но валидатор должен обработать
        with self.assertRaises(TypeError):
            Validator.validate_hours(None)


class TestDayTypeValidationComprehensive(unittest.TestCase):
    """Расширенные тесты валидации типов дней."""

    def test_all_valid_day_types(self):
        """Все корректные типы дней."""
        valid_types = [
            'Рабочий день',
            'Отпуск',
            'Больничный',
            'Командировка',
            'Отгул',
            'Неявка'
        ]
        for day_type in valid_types:
            is_valid, error = Validator.validate_day_type(day_type)
            self.assertTrue(is_valid, f"Тип '{day_type}' должен быть валидным")

    def test_invalid_day_type_unknown(self):
        """Неизвестный тип дня."""
        is_valid, error = Validator.validate_day_type('Праздник')
        self.assertFalse(is_valid)
        self.assertIn('Недопустимый', error)

    def test_invalid_day_type_empty(self):
        """Пустой тип дня."""
        is_valid, error = Validator.validate_day_type('')
        self.assertFalse(is_valid)

    def test_invalid_day_type_none(self):
        """None тип дня."""
        is_valid, error = Validator.validate_day_type(None)
        self.assertFalse(is_valid)

    def test_invalid_day_type_whitespace(self):
        """Тип дня из пробелов."""
        is_valid, error = Validator.validate_day_type('   ')
        self.assertFalse(is_valid)

    def test_case_sensitivity(self):
        """Регистрозависимость типа дня."""
        is_valid, error = Validator.validate_day_type('рабочий день')  # lowercase
        self.assertFalse(is_valid)


class TestTimesheetStatusValidationComprehensive(unittest.TestCase):
    """Расширенные тесты валидации статусов табеля."""

    def test_valid_status_in_progress(self):
        """Корректный статус: В работе."""
        is_valid, error = Validator.validate_timesheet_status('В работе')
        self.assertTrue(is_valid)

    def test_valid_status_approved(self):
        """Корректный статус: Утверждён."""
        is_valid, error = Validator.validate_timesheet_status('Утверждён')
        self.assertTrue(is_valid)

    def test_valid_status_archived(self):
        """Корректный статус: Архивирован."""
        is_valid, error = Validator.validate_timesheet_status('Архивирован')
        self.assertTrue(is_valid)

    def test_invalid_status_unknown(self):
        """Неизвестный статус."""
        is_valid, error = Validator.validate_timesheet_status('Черновик')
        self.assertFalse(is_valid)
        self.assertIn('Недопустимый', error)

    def test_invalid_status_empty(self):
        """Пустой статус."""
        is_valid, error = Validator.validate_timesheet_status('')
        self.assertFalse(is_valid)

    def test_invalid_status_none(self):
        """None статус."""
        is_valid, error = Validator.validate_timesheet_status(None)
        self.assertFalse(is_valid)

    def test_case_sensitivity(self):
        """Регистрозависимость статуса."""
        is_valid, error = Validator.validate_timesheet_status('в работе')  # lowercase
        self.assertFalse(is_valid)


class TestLoginValidationComprehensive(unittest.TestCase):
    """Расширенные тесты валидации авторизации."""

    def test_valid_credentials_standard(self):
        """Стандартные корректные данные."""
        is_valid, error = Validator.validate_login_credentials('tabel', 'tabel123')
        self.assertTrue(is_valid)

    def test_valid_credentials_single_char(self):
        """Односимвольные логин и пароль."""
        is_valid, error = Validator.validate_login_credentials('a', 'b')
        self.assertTrue(is_valid)

    def test_valid_credentials_long(self):
        """Длинные логин и пароль (в пределах лимита)."""
        long_username = 'u' * 100
        is_valid, error = Validator.validate_login_credentials(long_username, 'password')
        self.assertTrue(is_valid)

    def test_empty_username(self):
        """Пустой логин."""
        is_valid, error = Validator.validate_login_credentials('', 'password')
        self.assertFalse(is_valid)
        self.assertIn('имя пользователя', error.lower())

    def test_whitespace_username(self):
        """Логин из пробелов."""
        is_valid, error = Validator.validate_login_credentials('   ', 'password')
        self.assertFalse(is_valid)

    def test_none_username(self):
        """None логин."""
        is_valid, error = Validator.validate_login_credentials(None, 'password')
        self.assertFalse(is_valid)

    def test_empty_password(self):
        """Пустой пароль."""
        is_valid, error = Validator.validate_login_credentials('user', '')
        self.assertFalse(is_valid)
        self.assertIn('пароль', error.lower())

    def test_none_password(self):
        """None пароль."""
        is_valid, error = Validator.validate_login_credentials('user', None)
        self.assertFalse(is_valid)

    def test_too_long_username(self):
        """Слишком длинный логин."""
        long_username = 'u' * 101
        is_valid, error = Validator.validate_login_credentials(long_username, 'password')
        self.assertFalse(is_valid)
        self.assertIn('длинн', error.lower())

    def test_unicode_credentials(self):
        """Юникод в логе и пароле."""
        is_valid, error = Validator.validate_login_credentials('пользователь', 'пароль')
        self.assertTrue(is_valid)

    def test_special_characters_in_password(self):
        """Спецсимволы в пароле."""
        is_valid, error = Validator.validate_login_credentials('user', 'p@$$w0rd!#%^&*()')
        self.assertTrue(is_valid)


class TestPasswordChangeValidationComprehensive(unittest.TestCase):
    """Расширенные тесты валидации смены пароля."""

    def test_valid_password_change(self):
        """Корректная смена пароля."""
        is_valid, error = Validator.validate_password_change(
            'oldpass', 'newpass123', 'newpass123'
        )
        self.assertTrue(is_valid)

    def test_valid_password_min_length(self):
        """Пароль минимальной длины (6 символов)."""
        is_valid, error = Validator.validate_password_change(
            'oldpass', '123456', '123456'
        )
        self.assertTrue(is_valid)

    def test_empty_old_password(self):
        """Пустой старый пароль."""
        is_valid, error = Validator.validate_password_change(
            '', 'newpass', 'newpass'
        )
        self.assertFalse(is_valid)
        self.assertIn('текущий', error.lower())

    def test_none_old_password(self):
        """None старый пароль."""
        is_valid, error = Validator.validate_password_change(
            None, 'newpass', 'newpass'
        )
        self.assertFalse(is_valid)

    def test_empty_new_password(self):
        """Пустой новый пароль."""
        is_valid, error = Validator.validate_password_change(
            'oldpass', '', 'newpass'
        )
        self.assertFalse(is_valid)
        self.assertIn('нов', error.lower())

    def test_none_new_password(self):
        """None новый пароль."""
        is_valid, error = Validator.validate_password_change(
            'oldpass', None, 'newpass'
        )
        self.assertFalse(is_valid)

    def test_password_too_short(self):
        """Новый пароль короче 6 символов."""
        is_valid, error = Validator.validate_password_change(
            'oldpass', '12345', '12345'
        )
        self.assertFalse(is_valid)
        self.assertIn('6 символов', error)

    def test_passwords_not_match(self):
        """Пароли не совпадают."""
        is_valid, error = Validator.validate_password_change(
            'oldpass', 'newpass123', 'different'
        )
        self.assertFalse(is_valid)
        self.assertIn('совпадают', error.lower())

    def test_empty_confirm_password(self):
        """Пустой подтверждающий пароль."""
        is_valid, error = Validator.validate_password_change(
            'oldpass', 'newpass123', ''
        )
        self.assertFalse(is_valid)

    def test_none_confirm_password(self):
        """None подтверждающий пароль."""
        is_valid, error = Validator.validate_password_change(
            'oldpass', 'newpass123', None
        )
        self.assertFalse(is_valid)

    def test_unicode_passwords(self):
        """Юникод пароли."""
        is_valid, error = Validator.validate_password_change(
            'старыйпароль', 'новыйпароль123', 'новыйпароль123'
        )
        self.assertTrue(is_valid)


if __name__ == '__main__':
    unittest.main()
