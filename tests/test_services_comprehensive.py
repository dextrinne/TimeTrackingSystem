"""
Комплексные тесты всех сервисов: EmployeeService, TimesheetService, DocumentService, ReportService.
Покрывает: CRUD операции, поиск, бизнес-логика, генерация структур, подсчет итогов, экспорт.
Использует psycopg2 моки (без SQLite).
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.models import Employee, Timesheet, TimesheetEntry, Document
from services.employee_service import EmployeeService
from services.timesheet_service import TimesheetService
from services.document_service import DocumentService
from services.report_service import ReportService


class TestEmployeeServiceComprehensive(unittest.TestCase):
    """Комплексные тесты EmployeeService с моками."""

    def setUp(self):
        """Настройка: создание мока БД и сервиса."""
        self.mock_db = Mock()
        self.service = EmployeeService(self.mock_db)

    def test_get_all_employees_empty(self):
        """Получение сотрудников из пустой таблицы."""
        self.mock_db.execute_query.return_value = []
        employees = self.service.get_all_employees()
        self.assertEqual(len(employees), 0)

    def test_get_all_employees_multiple(self):
        """Получение нескольких сотрудников."""
        self.mock_db.execute_query.return_value = [
            (1, 'Иванов И.И.', 'Инженер', 1.0, 40),
            (2, 'Петров П.П.', 'Научный сотрудник', 0.5, 20),
        ]
        employees = self.service.get_all_employees()
        self.assertEqual(len(employees), 2)
        self.assertEqual(employees[0].fio, 'Иванов И.И.')
        self.assertEqual(employees[1].fio, 'Петров П.П.')

    def test_add_employee(self):
        """Добавление сотрудника."""
        emp = Employee(fio='Сидоров С.С.', position='Директор', rate=2.0, norm_hours=45)
        self.service.add_employee(emp)
        self.mock_db.execute_query.assert_called_once()
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('INSERT', call_args[0])
        self.assertIn('employee', call_args[0])

    def test_update_employee(self):
        """Обновление сотрудника."""
        emp = Employee(id_employee=1, fio='Обновлённый', position='Новая должность', rate=1.5, norm_hours=35)
        self.service.update_employee(emp)
        self.mock_db.execute_query.assert_called_once()
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('UPDATE', call_args[0])
        self.assertIn('employee', call_args[0])

    def test_delete_employee(self):
        """Удаление сотрудника."""
        self.service.delete_employee(5)
        self.mock_db.execute_query.assert_called_once()
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('DELETE', call_args[0])
        self.assertEqual(call_args[1], (5,))

    def test_get_employee_by_id(self):
        """Получение сотрудника по ID."""
        self.mock_db.execute_query.return_value = (1, 'Иванов И.И.', 'Инженер', 1.0, 40)
        emp = self.service.get_employee_by_id(1)
        self.assertIsNotNone(emp)
        self.assertEqual(emp.fio, 'Иванов И.И.')

    def test_get_employee_by_id_not_found(self):
        """Получение сотрудника по несуществующему ID."""
        self.mock_db.execute_query.return_value = None
        emp = self.service.get_employee_by_id(999)
        self.assertIsNone(emp)

    def test_search_employees_by_fio(self):
        """Поиск сотрудников по ФИО."""
        self.mock_db.execute_query.return_value = [(1, 'Иванов Иван Иванович', 'Инженер', 1.0, 40)]
        results = self.service.search_employees('Иванов')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].fio, 'Иванов Иван Иванович')

    def test_search_employees_no_results(self):
        """Поиск без результатов."""
        self.mock_db.execute_query.return_value = []
        results = self.service.search_employees('Несуществующий')
        self.assertEqual(len(results), 0)


class TestTimesheetServiceComprehensive(unittest.TestCase):
    """Комплексные тесты TimesheetService с моками."""

    def setUp(self):
        """Настройка: создание мока БД и сервиса."""
        self.mock_db = Mock()
        self.service = TimesheetService(self.mock_db)

    def test_create_timesheet(self):
        """Создание табеля."""
        self.mock_db.execute_query.return_value = (10,)
        ts_id = self.service.create_timesheet(date(2026, 3, 1), date(2026, 3, 31), 'В работе')
        self.assertEqual(ts_id, 10)
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('INSERT', call_args[0])
        self.assertIn('timesheet', call_args[0])

    def test_get_all_timesheets_empty(self):
        """Получение табелей из пустой таблицы."""
        self.mock_db.execute_query.return_value = []
        timesheets = self.service.get_all_timesheets()
        self.assertEqual(len(timesheets), 0)

    def test_get_all_timesheets_multiple(self):
        """Получение нескольких табелей."""
        from datetime import datetime
        self.mock_db.execute_query.return_value = [
            (1, date(2026, 3, 1), date(2026, 3, 31), 'В работе', datetime.now(), None, None),
            (2, date(2026, 2, 1), date(2026, 2, 28), 'Утверждён', datetime.now(), datetime.now(), None),
        ]
        timesheets = self.service.get_all_timesheets()
        self.assertEqual(len(timesheets), 2)

    def test_get_timesheet_by_id(self):
        """Получение табеля по ID."""
        from datetime import datetime
        self.mock_db.execute_query.return_value = (1, date(2026, 3, 1), date(2026, 3, 31), 'В работе', datetime.now(), None, None)
        ts = self.service.get_timesheet_by_id(1)
        self.assertIsNotNone(ts)
        self.assertEqual(ts.period_start, date(2026, 3, 1))

    def test_get_timesheet_by_id_not_found(self):
        """Получение табеля по несуществующему ID."""
        self.mock_db.execute_query.return_value = None
        ts = self.service.get_timesheet_by_id(999)
        self.assertIsNone(ts)

    def test_update_status_to_approved(self):
        """Изменение статуса на 'Утверждён'."""
        self.service.update_timesheet_status(1, 'Утверждён')
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('approved_at', call_args[0])

    def test_update_status_to_archived(self):
        """Изменение статуса на 'Архивирован'."""
        self.service.update_timesheet_status(1, 'Архивирован')
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('archived_at', call_args[0])

    def test_update_status_in_progress(self):
        """Изменение статуса на 'В работе'."""
        self.service.update_timesheet_status(1, 'В работе')
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('status', call_args[0])
        self.assertNotIn('approved_at', call_args[0])

    def test_delete_timesheet_success(self):
        """Удаление табеля с записями."""
        self.service.delete_timesheet(1)
        self.assertEqual(self.mock_db.execute_query.call_count, 2)
        calls = self.mock_db.execute_query.call_args_list
        self.assertIn('timesheet_entry', calls[0][0][0])
        self.assertIn('timesheet', calls[1][0][0])

    def test_delete_timesheet_failure(self):
        """Ошибка удаления табеля."""
        self.mock_db.execute_query.side_effect = Exception("FK violation")
        result = self.service.delete_timesheet(1)
        self.assertFalse(result)

    def test_add_entry(self):
        """Добавление записи в табель."""
        entry = TimesheetEntry(employee_id=1, timesheet_id=1, date=date(2026, 3, 2), hours_worked=8.0, type='Рабочий день')
        self.service.add_entry(entry)
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('INSERT', call_args[0])
        self.assertIn('timesheet_entry', call_args[0])

    def test_get_entries_by_timesheet(self):
        """Получение записей по табелю."""
        self.mock_db.execute_query.return_value = [
            (1, 1, 1, date(2026, 3, 2), 8.0, 'Рабочий день'),
            (2, 2, 1, date(2026, 3, 2), 7.0, 'Рабочий день'),
        ]
        entries = self.service.get_entries_by_timesheet(1)
        self.assertEqual(len(entries), 2)

    def test_calculate_employee_totals(self):
        """Подсчет итогов по сотруднику."""
        self.mock_db.execute_query.return_value = [
            ('Рабочий день', 5, 40.0),
            ('Отпуск', 3, 0.0),
            ('Больничный', 2, 0.0),
        ]
        totals = self.service.calculate_employee_totals(1, 1)
        self.assertEqual(totals['workdays'], 5)
        self.assertEqual(totals['vacations'], 3)
        self.assertEqual(totals['sick_leaves'], 2)
        self.assertEqual(totals['total_hours'], 40.0)

    def test_generate_timesheet_structure(self):
        """Автогенерация структуры табеля."""
        from datetime import datetime
        self.mock_db.execute_query.side_effect = [
            (1, date(2026, 3, 2), date(2026, 3, 6), 'В работе', datetime.now(), None, None),
            None,  # check existing entry - нет
            None,  # insert
            None,  # check
            None,  # insert
        ]
        self.service.generate_timesheet_structure(1, [1])
        # Проверяем что были вызовы INSERT
        self.assertTrue(self.mock_db.execute_query.called)


class TestDocumentServiceComprehensive(unittest.TestCase):
    """Комплексные тесты DocumentService с моками."""

    def setUp(self):
        """Настройка: создание мока БД и сервиса."""
        self.mock_db = Mock()
        self.service = DocumentService(self.mock_db)

    def test_add_document(self):
        """Добавление документа."""
        doc = Document(employee_id=1, type='Отпуск', start_date=date(2026, 3, 1), end_date=date(2026, 3, 14))
        self.service.add_document(doc)
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('INSERT', call_args[0])
        self.assertIn('document', call_args[0])

    def test_get_all_documents(self):
        """Получение всех документов."""
        self.mock_db.execute_query.return_value = [
            (1, 1, 'Отпуск', date(2026, 3, 1), date(2026, 3, 14)),
            (2, 2, 'Больничный', date(2026, 4, 1), date(2026, 4, 10)),
        ]
        docs = self.service.get_all_documents()
        self.assertEqual(len(docs), 2)
        self.assertEqual(docs[0].type, 'Отпуск')

    def test_get_documents_by_employee(self):
        """Получение документов сотрудника."""
        self.mock_db.execute_query.return_value = [(1, 1, 'Отпуск', date(2026, 3, 1), date(2026, 3, 14))]
        docs = self.service.get_documents_by_employee(1)
        self.assertEqual(len(docs), 1)

    def test_update_document(self):
        """Обновление документа."""
        doc = Document(id_document=1, employee_id=1, type='Командировка', start_date=date(2026, 3, 5), end_date=date(2026, 3, 10))
        self.service.update_document(doc)
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('UPDATE', call_args[0])
        self.assertIn('document', call_args[0])

    def test_delete_document(self):
        """Удаление документа."""
        self.service.delete_document(1)
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('DELETE', call_args[0])
        self.assertEqual(call_args[1], (1,))

    def test_get_documents_in_period(self):
        """Получение документов в периоде."""
        self.mock_db.execute_query.return_value = [(1, 1, 'Отпуск', date(2026, 3, 1), date(2026, 3, 14))]
        docs = self.service.get_documents_in_period(date(2026, 3, 1), date(2026, 3, 31))
        self.assertEqual(len(docs), 1)

    def test_is_employee_absent_true(self):
        """Проверка отсутствия сотрудника (истина)."""
        self.mock_db.execute_query.return_value = ('Отпуск',)
        is_absent, doc_type = self.service.is_employee_absent(1, date(2026, 3, 5))
        self.assertTrue(is_absent)
        self.assertEqual(doc_type, 'Отпуск')

    def test_is_employee_absent_false(self):
        """Проверка отсутствия сотрудника (ложь)."""
        self.mock_db.execute_query.return_value = None
        is_absent, doc_type = self.service.is_employee_absent(1, date(2026, 4, 1))
        self.assertFalse(is_absent)
        self.assertIsNone(doc_type)


class TestReportServiceComprehensive(unittest.TestCase):
    """Комплексные тесты ReportService с моками."""

    def setUp(self):
        """Настройка: создание мока БД и сервиса."""
        self.mock_db = Mock()
        self.service = ReportService(self.mock_db)

    def test_get_timesheet_report_empty(self):
        """Отчет по пустому табелю."""
        self.mock_db.execute_query.return_value = []
        report = self.service.get_timesheet_report(1)
        self.assertEqual(len(report), 0)

    def test_get_timesheet_report_with_data(self):
        """Отчет с данными."""
        self.mock_db.execute_query.return_value = [
            (1, 'Иванов И.И.', 'Инженер', 40, 20, 5, 2, 1, 0, 160.0),
            (2, 'Петров П.П.', 'Научный сотрудник', 20, 18, 3, 1, 0, 0, 126.0),
        ]
        report = self.service.get_timesheet_report(1)
        self.assertEqual(len(report), 2)
        self.assertEqual(report[0]['fio'], 'Иванов И.И.')
        self.assertEqual(report[0]['workdays'], 20)
        self.assertEqual(report[0]['total_hours'], 160.0)

    def test_get_employee_report(self):
        """Отчет по сотруднику."""
        self.mock_db.execute_query.side_effect = [
            ('Иванов И.И.', 'Инженер', 40),
            [(date(2026, 3, 2), 8.0, 'Рабочий день')],
        ]
        report = self.service.get_employee_report(1, date(2026, 3, 1), date(2026, 3, 31))
        self.assertIsNotNone(report)
        self.assertEqual(report['fio'], 'Иванов И.И.')

    def test_get_employee_report_not_found(self):
        """Отчет по несуществующему сотруднику."""
        self.mock_db.execute_query.return_value = None
        report = self.service.get_employee_report(999, date(2026, 3, 1), date(2026, 3, 31))
        self.assertIsNone(report)

    @patch('openpyxl.Workbook')
    def test_export_to_xlsx(self, mock_workbook):
        """Экспорт в XLSX."""
        mock_ws = Mock()
        mock_wb = Mock()
        mock_workbook.return_value = mock_wb
        mock_wb.active = mock_ws
        mock_ws.cell.return_value = Mock()

        self.mock_db.execute_query.side_effect = [
            [{'employee_id': 1, 'fio': 'Иванов И.И.', 'position': 'Инженер', 'norm_hours': 40,
              'workdays': 20, 'vacations': 5, 'sick_leaves': 2, 'business_trips': 1, 'absences': 0, 'total_hours': 160.0}],
            (date(2026, 3, 1), date(2026, 3, 31), 'В работе'),
        ]

        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            result = self.service.export_to_xlsx(1, f.name)
            self.assertTrue(result)
            mock_wb.save.assert_called_once()

    def test_export_to_xlsx_no_timesheet(self):
        """Экспорт несуществующего табеля."""
        self.mock_db.execute_query.side_effect = [[], None]
        result = self.service.export_to_xlsx(999, '/tmp/test.xlsx')
        self.assertFalse(result)

    def test_export_to_xlsx_exception(self):
        """Ошибка при экспорте."""
        self.mock_db.execute_query.side_effect = Exception("DB error")
        result = self.service.export_to_xlsx(1, '/tmp/test.xlsx')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
