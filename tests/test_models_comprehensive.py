"""
Комплексные тесты всех моделей данных.
Покрывает: Employee, Timesheet, TimesheetEntry, Document, User, ActivityLog, Report, Archive
+ Enum классы, сериализация/десериализация, пограничные случаи.
"""

import unittest
import sys
import os
from datetime import date, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.models import (
    Employee, Timesheet, TimesheetEntry, Document,
    User, ActivityLog, Report, Archive,
    TimesheetStatus, DayType, UserRole
)


class TestEmployeeModel(unittest.TestCase):
    """Расширенные тесты модели Employee."""

    def test_default_values(self):
        """Значения по умолчанию."""
        emp = Employee()
        self.assertIsNone(emp.id_employee)
        self.assertEqual(emp.fio, "")
        self.assertEqual(emp.position, "")
        self.assertEqual(emp.rate, 1.0)
        self.assertEqual(emp.norm_hours, 40)

    def test_custom_values(self):
        """Пользовательские значения."""
        emp = Employee(
            id_employee=5,
            fio='Петров Петр Петрович',
            position='Старший научный сотрудник',
            rate=1.5,
            norm_hours=35
        )
        self.assertEqual(emp.id_employee, 5)
        self.assertEqual(emp.fio, 'Петров Петр Петрович')
        self.assertEqual(emp.rate, 1.5)

    def test_to_dict(self):
        """Сериализация в словарь."""
        emp = Employee(id_employee=1, fio='Иванов И.И.', position='Инженер', rate=1.0, norm_hours=40)
        d = emp.to_dict()
        
        self.assertIsInstance(d, dict)
        self.assertEqual(d['id_employee'], 1)
        self.assertEqual(d['fio'], 'Иванов И.И.')
        self.assertEqual(d['position'], 'Инженер')
        self.assertEqual(d['rate'], 1.0)
        self.assertEqual(d['norm_hours'], 40)

    def test_from_row_full(self):
        """Десериализация из строки БД (полный набор данных)."""
        row = (1, 'Сидоров Сидор Сидорович', 'Директор', 2.0, 45)
        emp = Employee.from_row(row)
        
        self.assertEqual(emp.id_employee, 1)
        self.assertEqual(emp.fio, 'Сидоров Сидор Сидорович')
        self.assertEqual(emp.position, 'Директор')
        self.assertEqual(emp.rate, 2.0)
        self.assertEqual(emp.norm_hours, 45)

    def test_from_row_none(self):
        """Десериализация из None."""
        emp = Employee.from_row(None)
        self.assertIsNone(emp)

    def test_from_row_with_none_values(self):
        """Десериализация с None значениями."""
        row = (1, 'Иванов И.И.', None, None, None)
        emp = Employee.from_row(row)
        
        self.assertEqual(emp.id_employee, 1)
        self.assertEqual(emp.fio, 'Иванов И.И.')
        self.assertIsNone(emp.position)
        self.assertEqual(emp.rate, 0.0)  # None преобразуется в 0.0
        self.assertEqual(emp.norm_hours, 0)  # None преобразуется в 0

    def test_rate_edge_cases(self):
        """Пограничные значения ставки."""
        # Минимальная ставка
        emp1 = Employee(rate=0.0)
        self.assertEqual(emp1.rate, 0.0)
        
        # Очень маленькая ставка
        emp2 = Employee(rate=0.01)
        self.assertEqual(emp2.rate, 0.01)
        
        # Большая ставка
        emp3 = Employee(rate=999.99)
        self.assertEqual(emp3.rate, 999.99)

    def test_norm_hours_edge_cases(self):
        """Пограничные значения нормы часов."""
        # Минимальные часы
        emp1 = Employee(norm_hours=0)
        self.assertEqual(emp1.norm_hours, 0)
        
        # Стандартные часы
        emp2 = Employee(norm_hours=40)
        self.assertEqual(emp2.norm_hours, 40)
        
        # Максимальные часы
        emp3 = Employee(norm_hours=168)
        self.assertEqual(emp3.norm_hours, 168)

    def test_unicode_fio(self):
        """Юникод в ФИО."""
        unicode_fio = 'Иванов Иван Иванович'
        emp = Employee(fio=unicode_fio)
        self.assertEqual(emp.fio, unicode_fio)

    def test_long_fio(self):
        """Длинное ФИО."""
        long_fio = 'И' * 255
        emp = Employee(fio=long_fio)
        self.assertEqual(len(emp.fio), 255)

    def test_equality(self):
        """Сравнение объектов Employee."""
        emp1 = Employee(id_employee=1, fio='Иванов И.И.')
        emp2 = Employee(id_employee=1, fio='Иванов И.И.')
        emp3 = Employee(id_employee=2, fio='Петров П.П.')
        
        # Dataclass с одинаковыми полями равны
        self.assertEqual(emp1, emp2)
        self.assertNotEqual(emp1, emp3)


class TestTimesheetModel(unittest.TestCase):
    """Расширенные тесты модели Timesheet."""

    def test_default_values(self):
        """Значения по умолчанию."""
        ts = Timesheet()
        self.assertIsNone(ts.id_timesheet)
        self.assertIsInstance(ts.period_start, date)
        self.assertIsInstance(ts.period_end, date)
        self.assertEqual(ts.status, TimesheetStatus.IN_PROGRESS.value)
        self.assertIsInstance(ts.created_at, datetime)
        self.assertIsNone(ts.approved_at)
        self.assertIsNone(ts.archived_at)

    def test_custom_values(self):
        """Пользовательские значения."""
        ts = Timesheet(
            id_timesheet=10,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            status='Утверждён',
            approved_at=datetime(2026, 2, 1, 10, 0, 0)
        )
        self.assertEqual(ts.id_timesheet, 10)
        self.assertEqual(ts.status, 'Утверждён')
        self.assertIsNotNone(ts.approved_at)

    def test_to_dict(self):
        """Сериализация в словарь."""
        ts = Timesheet(
            id_timesheet=1,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            status='В работе'
        )
        d = ts.to_dict()
        
        self.assertEqual(d['id_timesheet'], 1)
        self.assertEqual(d['period_start'], date(2026, 3, 1))
        self.assertEqual(d['status'], 'В работе')

    def test_from_row_full(self):
        """Десериализация из строки БД."""
        now = datetime.now()
        row = (1, date(2026, 3, 1), date(2026, 3, 31), 'В работе', now, None, None)
        ts = Timesheet.from_row(row)
        
        self.assertEqual(ts.id_timesheet, 1)
        self.assertEqual(ts.period_start, date(2026, 3, 1))
        self.assertEqual(ts.status, 'В работе')
        self.assertEqual(ts.created_at, now)
        self.assertIsNone(ts.approved_at)

    def test_from_row_none(self):
        """Десериализация из None."""
        ts = Timesheet.from_row(None)
        self.assertIsNone(ts)

    def test_status_transitions(self):
        """Переходы статусов табеля."""
        ts = Timesheet()
        
        # Начальный статус
        self.assertEqual(ts.status, 'В работе')
        
        # Изменение на утверждён
        ts.status = 'Утверждён'
        ts.approved_at = datetime.now()
        self.assertEqual(ts.status, 'Утверждён')
        
        # Изменение на архивирован
        ts.status = 'Архивирован'
        ts.archived_at = datetime.now()
        self.assertEqual(ts.status, 'Архивирован')


class TestTimesheetEntryModel(unittest.TestCase):
    """Расширенные тесты модели TimesheetEntry."""

    def test_default_values(self):
        """Значения по умолчанию."""
        entry = TimesheetEntry()
        self.assertIsNone(entry.id_timesheet_entry)
        self.assertEqual(entry.employee_id, 0)
        self.assertEqual(entry.timesheet_id, 0)
        self.assertIsInstance(entry.date, date)
        self.assertEqual(entry.hours_worked, 0.0)
        self.assertEqual(entry.type, DayType.WORKDAY.value)

    def test_workday_entry(self):
        """Запись рабочего дня."""
        entry = TimesheetEntry(
            employee_id=1,
            timesheet_id=1,
            date=date(2026, 3, 2),
            hours_worked=8.0,
            type='Рабочий день'
        )
        self.assertEqual(entry.hours_worked, 8.0)
        self.assertEqual(entry.type, 'Рабочий день')

    def test_vacation_entry(self):
        """Запись отпуска."""
        entry = TimesheetEntry(
            employee_id=1,
            timesheet_id=1,
            date=date(2026, 3, 10),
            hours_worked=0.0,
            type='Отпуск'
        )
        self.assertEqual(entry.type, 'Отпуск')
        self.assertEqual(entry.hours_worked, 0.0)

    def test_sick_leave_entry(self):
        """Запись больничного."""
        entry = TimesheetEntry(
            employee_id=1,
            timesheet_id=1,
            date=date(2026, 3, 15),
            hours_worked=0.0,
            type='Больничный'
        )
        self.assertEqual(entry.type, 'Больничный')

    def test_to_dict(self):
        """Сериализация в словарь."""
        entry = TimesheetEntry(
            id_timesheet_entry=1,
            employee_id=5,
            timesheet_id=2,
            date=date(2026, 3, 5),
            hours_worked=7.5,
            type='Рабочий день'
        )
        d = entry.to_dict()
        
        self.assertEqual(d['employee_id'], 5)
        self.assertEqual(d['hours_worked'], 7.5)

    def test_from_row(self):
        """Десериализация из строки."""
        row = (1, 5, 2, date(2026, 3, 5), 7.5, 'Рабочий день')
        entry = TimesheetEntry.from_row(row)
        
        self.assertEqual(entry.id_timesheet_entry, 1)
        self.assertEqual(entry.hours_worked, 7.5)

    def test_from_row_none(self):
        """Десериализация из None."""
        entry = TimesheetEntry.from_row(None)
        self.assertIsNone(entry)

    def test_hours_variations(self):
        """Различные значения часов."""
        # Полные часы
        entry1 = TimesheetEntry(hours_worked=8.0)
        self.assertEqual(entry1.hours_worked, 8.0)
        
        # Половинки
        entry2 = TimesheetEntry(hours_worked=0.5)
        self.assertEqual(entry2.hours_worked, 0.5)
        
        # Нулевые часы
        entry3 = TimesheetEntry(hours_worked=0.0)
        self.assertEqual(entry3.hours_worked, 0.0)


class TestDocumentModel(unittest.TestCase):
    """Расширенные тесты модели Document."""

    def test_default_values(self):
        """Значения по умолчанию."""
        doc = Document()
        self.assertIsNone(doc.id_document)
        self.assertEqual(doc.employee_id, 0)
        self.assertEqual(doc.type, "")
        self.assertIsInstance(doc.start_date, date)
        self.assertIsInstance(doc.end_date, date)

    def test_vacation_document(self):
        """Документ отпуска."""
        doc = Document(
            id_document=1,
            employee_id=5,
            type='Отпуск',
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 14)
        )
        self.assertEqual(doc.type, 'Отпуск')
        self.assertEqual(doc.employee_id, 5)

    def test_sick_leave_document(self):
        """Документ больничного."""
        doc = Document(
            employee_id=3,
            type='Больничный',
            start_date=date(2026, 4, 10),
            end_date=date(2026, 4, 20)
        )
        self.assertEqual(doc.type, 'Больничный')

    def test_business_trip_document(self):
        """Документ командировки."""
        doc = Document(
            employee_id=7,
            type='Командировка',
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5)
        )
        self.assertEqual(doc.type, 'Командировка')

    def test_day_off_document(self):
        """Документ отгула."""
        doc = Document(
            employee_id=2,
            type='Отгул',
            start_date=date(2026, 6, 15),
            end_date=date(2026, 6, 15)
        )
        self.assertEqual(doc.type, 'Отгул')
        # Один день
        self.assertEqual(doc.start_date, doc.end_date)

    def test_to_dict(self):
        """Сериализация в словарь."""
        doc = Document(
            id_document=10,
            employee_id=5,
            type='Отпуск',
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 14)
        )
        d = doc.to_dict()
        
        self.assertEqual(d['id_document'], 10)
        self.assertEqual(d['type'], 'Отпуск')
        self.assertEqual(d['start_date'], date(2026, 7, 1))

    def test_from_row(self):
        """Десериализация из строки."""
        row = (1, 5, 'Отпуск', date(2026, 3, 1), date(2026, 3, 14))
        doc = Document.from_row(row)
        
        self.assertEqual(doc.id_document, 1)
        self.assertEqual(doc.type, 'Отпуск')

    def test_from_row_none(self):
        """Десериализация из None."""
        doc = Document.from_row(None)
        self.assertIsNone(doc)

    def test_single_day_document(self):
        """Документ на один день."""
        doc = Document(
            employee_id=1,
            type='Отгул',
            start_date=date(2026, 8, 15),
            end_date=date(2026, 8, 15)
        )
        # start_date == end_date - допустимо
        self.assertEqual(doc.start_date, doc.end_date)


class TestUserModel(unittest.TestCase):
    """Тесты модели User."""

    def test_default_values(self):
        """Значения по умолчанию."""
        user = User()
        self.assertIsNone(user.id_user)
        self.assertEqual(user.username, "")
        self.assertEqual(user.password_hash, "")
        self.assertEqual(user.role, UserRole.TABELSHCHIK.value)
        self.assertIsNone(user.employee_id)
        self.assertIsInstance(user.created_at, datetime)

    def test_custom_user(self):
        """Пользовательский пользователь."""
        user = User(
            id_user=1,
            username='tabel',
            password_hash='abc123hash',
            role='Табельщик',
            employee_id=5
        )
        self.assertEqual(user.username, 'tabel')
        self.assertEqual(user.role, 'Табельщик')
        self.assertEqual(user.employee_id, 5)

    def test_from_row(self):
        """Десериализация из строки."""
        now = datetime.now()
        row = (1, 'admin', 'hash123', 'Табельщик', 5, now)
        user = User.from_row(row)
        
        self.assertEqual(user.id_user, 1)
        self.assertEqual(user.username, 'admin')
        self.assertEqual(user.employee_id, 5)
        self.assertEqual(user.created_at, now)

    def test_from_row_none(self):
        """Десериализация из None."""
        user = User.from_row(None)
        self.assertIsNone(user)


class TestActivityLogModel(unittest.TestCase):
    """Тесты модели ActivityLog."""

    def test_default_values(self):
        """Значения по умолчанию."""
        log = ActivityLog()
        self.assertIsNone(log.id_log)
        self.assertIsNone(log.user_id)
        self.assertEqual(log.action, "")
        self.assertEqual(log.entity_type, "")
        self.assertIsNone(log.entity_id)
        self.assertEqual(log.description, "")
        self.assertIsInstance(log.created_at, datetime)

    def test_custom_log(self):
        """Пользовательская запись журнала."""
        log = ActivityLog(
            id_log=1,
            user_id=5,
            action='CREATE',
            entity_type='employee',
            entity_id=10,
            description='Создан новый сотрудник'
        )
        self.assertEqual(log.action, 'CREATE')
        self.assertEqual(log.entity_type, 'employee')

    def test_from_row(self):
        """Десериализация из строки."""
        now = datetime.now()
        row = (1, 5, 'UPDATE', 'timesheet', 3, 'Обновлен табель', now)
        log = ActivityLog.from_row(row)
        
        self.assertEqual(log.id_log, 1)
        self.assertEqual(log.action, 'UPDATE')
        self.assertEqual(log.entity_type, 'timesheet')
        self.assertEqual(log.entity_id, 3)

    def test_from_row_none(self):
        """Десериализация из None."""
        log = ActivityLog.from_row(None)
        self.assertIsNone(log)


class TestReportModel(unittest.TestCase):
    """Расширенные тесты модели Report."""

    def test_default_values(self):
        """Значения по умолчанию."""
        report = Report()
        self.assertIsNone(report.id_report)
        self.assertEqual(report.timesheet_id, 0)
        self.assertIsInstance(report.period_start, date)
        self.assertIsInstance(report.period_end, date)
        self.assertIsInstance(report.generated_at, datetime)
        self.assertIsInstance(report.data, list)
        self.assertEqual(len(report.data), 0)

    def test_report_with_data(self):
        """Отчет с данными."""
        report_data = [
            {'fio': 'Иванов И.И.', 'total_hours': 160, 'workdays': 20},
            {'fio': 'Петров П.П.', 'total_hours': 140, 'workdays': 18}
        ]
        report = Report(
            timesheet_id=1,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            data=report_data
        )
        self.assertEqual(len(report.data), 2)
        self.assertEqual(report.data[0]['fio'], 'Иванов И.И.')

    def test_to_dict(self):
        """Сериализация в словарь."""
        report = Report(
            id_report=5,
            timesheet_id=2,
            period_start=date(2026, 4, 1),
            period_end=date(2026, 4, 30),
            data=[{'employee': 'Test', 'hours': 100}]
        )
        d = report.to_dict()
        
        self.assertEqual(d['id_report'], 5)
        self.assertEqual(len(d['data']), 1)

    def test_empty_report(self):
        """Пустой отчет."""
        report = Report()
        d = report.to_dict()
        self.assertEqual(d['data'], [])


class TestArchiveModel(unittest.TestCase):
    """Расширенные тесты модели Archive."""

    def test_default_values(self):
        """Значения по умолчанию."""
        arch = Archive()
        self.assertIsNone(arch.id_archive)
        self.assertEqual(arch.timesheet_id, 0)
        self.assertIsInstance(arch.archived_at, datetime)
        self.assertIsInstance(arch.period_start, date)
        self.assertIsInstance(arch.period_end, date)
        self.assertEqual(arch.comment, "")

    def test_custom_archive(self):
        """Пользовательский архив."""
        arch = Archive(
            id_archive=1,
            timesheet_id=10,
            archived_at=datetime(2026, 4, 1, 12, 0, 0),
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            comment='Архив за март 2026'
        )
        self.assertEqual(arch.comment, 'Архив за март 2026')

    def test_from_row_full(self):
        """Десериализация из строки (полная)."""
        now = datetime.now()
        row = (1, 10, now, date(2026, 3, 1), date(2026, 3, 31), 'Комментарий')
        arch = Archive.from_row(row)
        
        self.assertEqual(arch.timesheet_id, 10)
        self.assertEqual(arch.comment, 'Комментарий')

    def test_from_row_missing_fields(self):
        """Десериализация с отсутствующими полями."""
        row = (1, 10, datetime.now(), date(2026, 3, 1), date(2026, 3, 31))
        arch = Archive.from_row(row)
        
        self.assertEqual(arch.comment, "")  # Значение по умолчанию

    def test_from_row_none(self):
        """Десериализация из None."""
        arch = Archive.from_row(None)
        self.assertIsNone(arch)


class TestEnums(unittest.TestCase):
    """Тесты перечислений."""

    def test_timesheet_status_values(self):
        """Значения статусов табеля."""
        self.assertEqual(TimesheetStatus.IN_PROGRESS.value, "В работе")
        self.assertEqual(TimesheetStatus.APPROVED.value, "Утверждён")
        self.assertEqual(TimesheetStatus.ARCHIVED.value, "Архивирован")

    def test_day_type_values(self):
        """Значения типов дней."""
        self.assertEqual(DayType.WORKDAY.value, "Рабочий день")
        self.assertEqual(DayType.VACATION.value, "Отпуск")
        self.assertEqual(DayType.SICK_LEAVE.value, "Больничный")
        self.assertEqual(DayType.BUSINESS_TRIP.value, "Командировка")
        self.assertEqual(DayType.DAY_OFF.value, "Отгул")
        self.assertEqual(DayType.ABSENT.value, "Неявка")

    def test_user_role_values(self):
        """Значения ролей пользователей."""
        self.assertEqual(UserRole.TABELSHCHIK.value, "Табельщик")

    def test_enum_uniqueness(self):
        """Уникальность значений перечислений."""
        # Проверяем что все значения статусов уникальны
        status_values = [s.value for s in TimesheetStatus]
        self.assertEqual(len(status_values), len(set(status_values)))
        
        # Проверяем что все значения типов дней уникальны
        day_type_values = [d.value for d in DayType]
        self.assertEqual(len(day_type_values), len(set(day_type_values)))


if __name__ == '__main__':
    unittest.main()
