"""
Модульные тесты моделей данных (ЛР1: календарный план — тестирование).
"""

import unittest
import sys
import os
from datetime import date, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.models import Employee, Timesheet, TimesheetEntry, Document, Report, Archive


class TestEmployee(unittest.TestCase):
    """Тесты модели Employee."""

    def test_default_values(self):
        """Значения по умолчанию."""
        emp = Employee()
        self.assertEqual(emp.fio, "")
        self.assertEqual(emp.rate, 1.0)
        self.assertEqual(emp.norm_hours, 40)

    def test_to_dict(self):
        """Сериализация в словарь."""
        emp = Employee(id_employee=1, fio='Иванов И.И.', position='Сотрудник', rate=1.0, norm_hours=40)
        d = emp.to_dict()
        self.assertEqual(d['fio'], 'Иванов И.И.')
        self.assertEqual(d['norm_hours'], 40)

    def test_from_row(self):
        """Десериализация из строки БД."""
        emp = Employee.from_row((1, 'Петров П.П.', 'Инженер', 0.5, 20))
        self.assertEqual(emp.fio, 'Петров П.П.')
        self.assertEqual(emp.rate, 0.5)


class TestTimesheet(unittest.TestCase):
    """Тесты модели Timesheet."""

    def test_default_status(self):
        """Статус по умолчанию."""
        ts = Timesheet()
        self.assertEqual(ts.status, 'В работе')

    def test_from_row(self):
        """Десериализация из строки БД."""
        ts = Timesheet.from_row((1, date(2026, 3, 1), date(2026, 3, 31), 'В работе',
                                  datetime.now(), None, None))
        self.assertEqual(ts.period_start, date(2026, 3, 1))
        self.assertEqual(ts.status, 'В работе')


class TestTimesheetEntry(unittest.TestCase):
    """Тесты модели TimesheetEntry."""

    def test_default_hours(self):
        """Часы по умолчанию."""
        entry = TimesheetEntry()
        self.assertEqual(entry.hours_worked, 0.0)

    def test_from_row(self):
        """Десериализация из строки БД."""
        entry = TimesheetEntry.from_row((1, 1, 1, date(2026, 3, 2), 8.0, 'Рабочий день'))
        self.assertEqual(entry.hours_worked, 8.0)
        self.assertEqual(entry.type, 'Рабочий день')


class TestDocument(unittest.TestCase):
    """Тесты модели Document."""

    def test_from_row(self):
        """Десериализация из строки БД."""
        doc = Document.from_row((1, 1, 'Отпуск', date(2026, 3, 1), date(2026, 3, 14)))
        self.assertEqual(doc.type, 'Отпуск')
        self.assertEqual(doc.start_date, date(2026, 3, 1))


class TestReport(unittest.TestCase):
    """Тесты модели Report (ЛР2 абстракция)."""

    def test_to_dict(self):
        """Сериализация в словарь."""
        report = Report(
            timesheet_id=1,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            data=[{'fio': 'Иванов И.И.', 'total_hours': 160}]
        )
        d = report.to_dict()
        self.assertEqual(d['timesheet_id'], 1)
        self.assertEqual(len(d['data']), 1)


class TestArchive(unittest.TestCase):
    """Тесты модели Archive (ЛР2 абстракция)."""

    def test_from_row(self):
        """Десериализация из строки БД."""
        arch = Archive.from_row((1, 1, datetime.now(), date(2026, 3, 1), date(2026, 3, 31), 'Архив за март'))
        self.assertEqual(arch.timesheet_id, 1)
        self.assertEqual(arch.comment, 'Архив за март')


if __name__ == '__main__':
    unittest.main()
