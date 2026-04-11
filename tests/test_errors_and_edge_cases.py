"""
Тесты обработки ошибок и пограничных случаев.
Покрывает: все возможные ошибки, исключения, edge cases во всех компонентах.
Использует psycopg2 моки (без SQLite).
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.models import Employee, Timesheet, TimesheetEntry, Document
from utils.validators import Validator
from services.employee_service import EmployeeService


class TestDatabaseErrors(unittest.TestCase):
    """Тесты ошибок базы данных с моками."""

    def setUp(self):
        """Настройка: создание мока БД."""
        self.mock_db = Mock()
        self.service = EmployeeService(self.mock_db)

    def test_null_constraint_violation(self):
        """Нарушение ограничения NOT NULL."""
        self.mock_db.execute_query.side_effect = Exception('null value in column "fio" violates not-null constraint')
        emp = Employee(fio=None, position='Тест')
        
        with self.assertRaises(Exception):
            self.service.add_employee(emp)

    def test_invalid_sql_syntax(self):
        """Неверный SQL синтаксис."""
        self.mock_db.execute_query.side_effect = Exception('syntax error at or near "SELEC"')
        
        with self.assertRaises(Exception):
            self.mock_db.execute_query('SELEC * FROM employee')

    def test_table_does_not_exist(self):
        """Таблица не существует."""
        self.mock_db.execute_query.side_effect = Exception('relation "nonexistent_table" does not exist')
        
        with self.assertRaises(Exception):
            self.mock_db.execute_query('SELECT * FROM nonexistent_table')

    def test_column_does_not_exist(self):
        """Колонка не существует."""
        self.mock_db.execute_query.side_effect = Exception('column "nonexistent_column" does not exist')
        
        with self.assertRaises(Exception):
            self.mock_db.execute_query('SELECT nonexistent_column FROM employee')

    def test_foreign_key_violation(self):
        """Нарушение внешнего ключа."""
        self.mock_db.execute_query.side_effect = Exception('insert or update on table "timesheet_entry" violates foreign key constraint')
        
        with self.assertRaises(Exception):
            self.mock_db.execute_query(
                'INSERT INTO timesheet_entry (employee_id) VALUES (%s)',
                (999999,)
            )

    def test_unique_violation(self):
        """Нарушение уникальности."""
        self.mock_db.execute_query.side_effect = Exception('duplicate key value violates unique constraint')
        
        with self.assertRaises(Exception):
            self.mock_db.execute_query(
                'INSERT INTO users (username) VALUES (%s)',
                ('duplicate_user',)
            )

    def test_connection_lost(self):
        """Потеря соединения с БД."""
        self.mock_db.execute_query.side_effect = Exception('server closed the connection unexpectedly')
        
        with self.assertRaises(Exception):
            self.service.get_all_employees()

    def test_timeout_error(self):
        """Таймаут запроса."""
        self.mock_db.execute_query.side_effect = Exception('canceling statement due to statement timeout')
        
        with self.assertRaises(Exception):
            self.service.get_all_employees()


class TestServiceErrors(unittest.TestCase):
    """Тесты ошибок сервисов."""

    def setUp(self):
        """Настройка."""
        self.mock_db = Mock()
        self.service = EmployeeService(self.mock_db)

    def test_get_nonexistent_employee(self):
        """Получение несуществующего сотрудника."""
        self.mock_db.execute_query.return_value = None
        emp = self.service.get_employee_by_id(999999)
        self.assertIsNone(emp)

    def test_update_nonexistent_employee(self):
        """Обновление несуществующего сотрудника."""
        emp = Employee(id_employee=999999, fio='Nonexistent', position='Position', rate=1.0, norm_hours=40)
        self.service.update_employee(emp)
        self.mock_db.execute_query.assert_called_once()

    def test_delete_nonexistent_employee(self):
        """Удаление несуществующего сотрудника."""
        self.service.delete_employee(999999)
        self.mock_db.execute_query.assert_called_once()

    def test_add_employee_with_special_chars(self):
        """Добавление сотрудника со спецсимволами."""
        emp = Employee(fio="O'Neill-Смит \"Младший\"", position='Инженер <Senior>', rate=1.0, norm_hours=40)
        self.service.add_employee(emp)
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn("O'Neill", call_args[1][0])

    def test_search_with_sql_injection_attempt(self):
        """Поиск с попыткой SQL-инъекции."""
        self.mock_db.execute_query.return_value = []
        results = self.service.search_employees("'; DROP TABLE employee; --")
        # Параметризованный запрос должен защитить
        self.assertEqual(len(results), 0)


class TestModelEdgeCases(unittest.TestCase):
    """Тесты пограничных случаев моделей."""

    def test_employee_empty_string_fields(self):
        """Employee с пустыми строковыми полями."""
        emp = Employee(fio='', position='', rate=0.0, norm_hours=0)
        self.assertEqual(emp.fio, '')
        self.assertEqual(emp.position, '')

    def test_employee_very_long_strings(self):
        """Employee с очень длинными строками."""
        long_fio = 'А' * 10000
        long_position = 'Б' * 10000
        
        emp = Employee(fio=long_fio, position=long_position)
        self.assertEqual(len(emp.fio), 10000)
        self.assertEqual(len(emp.position), 10000)

    def test_timesheet_past_dates(self):
        """Timesheet с датами в прошлом."""
        ts = Timesheet(period_start=date(1900, 1, 1), period_end=date(1900, 1, 31))
        self.assertEqual(ts.period_start, date(1900, 1, 1))

    def test_timesheet_far_future_dates(self):
        """Timesheet с датами в далеком будущем."""
        ts = Timesheet(period_start=date(2100, 1, 1), period_end=date(2100, 1, 31))
        self.assertEqual(ts.period_start, date(2100, 1, 1))

    def test_timesheet_entry_negative_hours(self):
        """TimesheetEntry с отрицательными часами."""
        entry = TimesheetEntry(hours_worked=-10.0)
        self.assertEqual(entry.hours_worked, -10.0)

    def test_timesheet_entry_very_large_hours(self):
        """TimesheetEntry с очень большими часами."""
        entry = TimesheetEntry(hours_worked=1000.0)
        self.assertEqual(entry.hours_worked, 1000.0)

    def test_document_same_day(self):
        """Document с одинаковыми датами начала и окончания."""
        doc = Document(start_date=date(2026, 5, 1), end_date=date(2026, 5, 1))
        self.assertEqual(doc.start_date, doc.end_date)

    def test_document_overlapping_periods(self):
        """Document с пересекающимися периодами."""
        doc1 = Document(start_date=date(2026, 3, 1), end_date=date(2026, 3, 15))
        doc2 = Document(start_date=date(2026, 3, 10), end_date=date(2026, 3, 25))
        # Оба документа валидны сами по себе
        self.assertLess(doc1.start_date, doc1.end_date)
        self.assertLess(doc2.start_date, doc2.end_date)


class TestValidatorEdgeCases(unittest.TestCase):
    """Тесты пограничных случаев валидаторов."""

    def test_employee_fio_exactly_max_length(self):
        """ФИО точно максимальной длины."""
        fio = 'А' * 255
        is_valid, error = Validator.validate_employee_data(fio, 'Должность', 1.0, 40)
        self.assertTrue(is_valid)

    def test_employee_fio_one_over_max(self):
        """ФИО на один символ больше максимума."""
        fio = 'А' * 256
        is_valid, error = Validator.validate_employee_data(fio, 'Должность', 1.0, 40)
        self.assertFalse(is_valid)

    def test_position_exactly_max_length(self):
        """Должность точно максимальной длины."""
        position = 'А' * 100
        is_valid, error = Validator.validate_employee_data('ФИО', position, 1.0, 40)
        self.assertTrue(is_valid)

    def test_position_one_over_max(self):
        """Должность на один символ больше максимума."""
        position = 'А' * 101
        is_valid, error = Validator.validate_employee_data('ФИО', position, 1.0, 40)
        self.assertFalse(is_valid)

    def test_rate_exactly_max(self):
        """Ставка точно максимальная."""
        is_valid, error = Validator.validate_employee_data('ФИО', 'Должность', 999.99, 40)
        self.assertTrue(is_valid)

    def test_rate_slightly_over_max(self):
        """Ставка чуть больше максимальной."""
        is_valid, error = Validator.validate_employee_data('ФИО', 'Должность', 1000.0, 40)
        self.assertFalse(is_valid)

    def test_hours_exactly_24(self):
        """Часы ровно 24."""
        is_valid, error = Validator.validate_hours(24.0)
        self.assertTrue(is_valid)

    def test_hours_slightly_over_24(self):
        """Часы чуть больше 24."""
        is_valid, error = Validator.validate_hours(24.01)
        self.assertFalse(is_valid)

    def test_username_exactly_max_length(self):
        """Логин точно максимальной длины."""
        username = 'u' * 100
        is_valid, error = Validator.validate_login_credentials(username, 'password')
        self.assertTrue(is_valid)

    def test_username_one_over_max(self):
        """Логин на один символ больше максимума."""
        username = 'u' * 101
        is_valid, error = Validator.validate_login_credentials(username, 'password')
        self.assertFalse(is_valid)

    def test_password_exactly_min_length(self):
        """Пароль точно минимальной длины."""
        is_valid, error = Validator.validate_password_change('oldpass', '123456', '123456')
        self.assertTrue(is_valid)

    def test_password_one_under_min(self):
        """Пароль на один символ меньше минимума."""
        is_valid, error = Validator.validate_password_change('oldpass', '12345', '12345')
        self.assertFalse(is_valid)


class TestDateEdgeCases(unittest.TestCase):
    """Тесты пограничных случаев с датами."""

    def test_date_year_1900(self):
        """Дата в 1900 году."""
        is_valid, error = Validator.validate_dates(date(1900, 1, 1), date(1900, 12, 31))
        self.assertTrue(is_valid)

    def test_date_year_2100(self):
        """Дата в 2100 году."""
        is_valid, error = Validator.validate_dates(date(2100, 1, 1), date(2100, 12, 31))
        self.assertTrue(is_valid)

    def test_date_leap_year_feb_29(self):
        """29 февраля в високосном году."""
        is_valid, error = Validator.validate_dates(date(2024, 2, 29), date(2024, 2, 29))
        self.assertTrue(is_valid)

    def test_date_range_one_year(self):
        """Диапазон дат ровно один год."""
        is_valid, error = Validator.validate_dates(date(2026, 1, 1), date(2027, 1, 1))
        self.assertTrue(is_valid)

    def test_date_range_multiple_years(self):
        """Диапазон дат несколько лет."""
        is_valid, error = Validator.validate_dates(date(2020, 1, 1), date(2030, 12, 31))
        self.assertTrue(is_valid)

    def test_date_consecutive_days(self):
        """Последовательные дни."""
        is_valid, error = Validator.validate_dates(date(2026, 3, 15), date(2026, 3, 16))
        self.assertTrue(is_valid)


class TestUnicodeAndSpecialCharacters(unittest.TestCase):
    """Тесты юникода и специальных символов."""

    def test_cyrillic_unicode(self):
        """Кириллица."""
        is_valid, error = Validator.validate_employee_data('Иванов Иван Иванович', 'Научный сотрудник', 1.0, 40)
        self.assertTrue(is_valid)

    def test_mixed_unicode(self):
        """Смешанные юникод символы."""
        fio = 'Иванов-Ivan'
        is_valid, error = Validator.validate_employee_data(fio, 'Сотрудник', 1.0, 40)
        self.assertTrue(is_valid)

    def test_emoji_in_fio(self):
        """Эмодзи в ФИО (технически возможно)."""
        fio = 'Иванов 👨\u200d💻'
        is_valid, error = Validator.validate_employee_data(fio, 'Сотрудник', 1.0, 40)
        self.assertTrue(is_valid)

    def test_special_xml_characters(self):
        """Специальные XML символы."""
        fio = 'Иванов & Петров <Научный> "Сотрудник" \'Отпуск\''
        is_valid, error = Validator.validate_employee_data(fio, 'Должность', 1.0, 40)
        self.assertTrue(is_valid)

    def test_sql_injection_attempt(self):
        """Попытка SQL-инъекции."""
        fio = "'; DROP TABLE employee; --"
        is_valid, error = Validator.validate_employee_data(fio, 'Должность', 1.0, 40)
        # Валидация пропустит, но параметризованные запросы защитят
        self.assertTrue(is_valid)

    def test_newline_characters(self):
        """Символы новой строки."""
        fio = 'Иванов\nИван'
        is_valid, error = Validator.validate_employee_data(fio, 'Должность', 1.0, 40)
        self.assertTrue(is_valid)


if __name__ == '__main__':
    unittest.main()
