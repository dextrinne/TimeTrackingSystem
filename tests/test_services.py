"""
Интеграционные тесты сервисов (ЛР1: календарный план — тестирование).
Тесты используют моки psycopg2 (без SQLite).
"""

import unittest
import sys
import os
from unittest.mock import Mock
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.models import Employee, Timesheet, Document, TimesheetEntry
from services.employee_service import EmployeeService
from services.timesheet_service import TimesheetService
from services.document_service import DocumentService


class TestEmployeeService(unittest.TestCase):
    """Тесты сервиса сотрудников с моками."""

    def setUp(self):
        """Создание мока БД и сервиса."""
        self.mock_db = Mock()
        self.service = EmployeeService(self.mock_db)

    def test_create_employee(self):
        """Создание сотрудника."""
        emp = Employee(fio='Иванов Иван Иванович', position='Инженер', rate=1.0, norm_hours=40)
        self.service.add_employee(emp)
        self.mock_db.execute_query.assert_called_once()
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('INSERT', call_args[0])

    def test_read_employee(self):
        """Чтение сотрудника."""
        self.mock_db.execute_query.return_value = (1, 'Петров П.П.', 'Инженер', 1.0, 40)
        emp = self.service.get_employee_by_id(1)
        self.assertEqual(emp.fio, 'Петров П.П.')

    def test_update_employee(self):
        """Обновление сотрудника."""
        emp = Employee(id_employee=1, fio='Сидоров С.С. обновлённый', position='Старший сотрудник', rate=1.0, norm_hours=40)
        self.service.update_employee(emp)
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('UPDATE', call_args[0])

    def test_delete_employee(self):
        """Удаление сотрудника."""
        self.service.delete_employee(1)
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('DELETE', call_args[0])
        self.assertEqual(call_args[1], (1,))


class TestTimesheetService(unittest.TestCase):
    """Тесты сервиса табелей с моками."""

    def setUp(self):
        """Создание мока БД и сервиса."""
        self.mock_db = Mock()
        self.service = TimesheetService(self.mock_db)

    def test_create_timesheet(self):
        """Создание табеля."""
        self.mock_db.execute_query.return_value = (1,)
        ts_id = self.service.create_timesheet(date(2026, 3, 1), date(2026, 3, 31))
        self.assertGreater(ts_id, 0)

    def test_update_status(self):
        """Изменение статуса табеля."""
        self.service.update_timesheet_status(1, 'Утверждён')
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('approved_at', call_args[0])

    def test_add_entry(self):
        """Добавление записи табеля."""
        entry = TimesheetEntry(employee_id=1, timesheet_id=1, date=date(2026, 3, 2), hours_worked=8.0, type='Рабочий день')
        self.service.add_entry(entry)
        self.mock_db.execute_query.assert_called_once()


class TestDocumentService(unittest.TestCase):
    """Тесты сервиса документов с моками."""

    def setUp(self):
        """Создание мока БД и сервиса."""
        self.mock_db = Mock()
        self.service = DocumentService(self.mock_db)

    def test_create_document(self):
        """Создание документа (отпуск)."""
        doc = Document(employee_id=1, type='Отпуск', start_date=date(2026, 3, 1), end_date=date(2026, 3, 14))
        self.service.add_document(doc)
        self.mock_db.execute_query.assert_called_once()
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('INSERT', call_args[0])

    def test_delete_document(self):
        """Удаление документа."""
        self.service.delete_document(1)
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('DELETE', call_args[0])


if __name__ == '__main__':
    unittest.main()
