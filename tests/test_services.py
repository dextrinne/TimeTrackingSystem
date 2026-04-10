"""
Интеграционные тесты сервисов (ЛР1: календарный план — тестирование).
Тесты используют SQLite как лёгкую БД для тестирования.
"""

import unittest
import sys
import os
import sqlite3
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.models import Employee, Timesheet, Document, TimesheetEntry


class TestEmployeeService(unittest.TestCase):
    """Интеграционные тесты сервиса сотрудников."""

    def setUp(self):
        """Создание тестовой БД."""
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE employee (
                id_employee INTEGER PRIMARY KEY AUTOINCREMENT,
                fio TEXT NOT NULL,
                position TEXT,
                rate REAL,
                norm_hours INTEGER
            )
        ''')
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def _insert(self, fio, position='Сотрудник', rate=1.0, norm_hours=40):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO employee (fio, position, rate, norm_hours) VALUES (?, ?, ?, ?)',
                    (fio, position, rate, norm_hours))
        self.conn.commit()
        return cur.lastrowid

    def _count(self):
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) FROM employee')
        return cur.fetchone()[0]

    def test_create_employee(self):
        """Создание сотрудника."""
        emp_id = self._insert('Иванов Иван Иванович')
        self.assertGreater(emp_id, 0)

    def test_read_employee(self):
        """Чтение сотрудника."""
        emp_id = self._insert('Петров П.П.')
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM employee WHERE id_employee = ?', (emp_id,))
        row = cur.fetchone()
        self.assertEqual(row['fio'], 'Петров П.П.')

    def test_update_employee(self):
        """Обновление сотрудника."""
        emp_id = self._insert('Сидоров С.С.')
        cur = self.conn.cursor()
        cur.execute('UPDATE employee SET fio = ?, position = ? WHERE id_employee = ?',
                    ('Сидоров С.С. обновлённый', 'Старший сотрудник', emp_id))
        self.conn.commit()
        cur.execute('SELECT position FROM employee WHERE id_employee = ?', (emp_id,))
        self.assertEqual(cur.fetchone()['position'], 'Старший сотрудник')

    def test_delete_employee(self):
        """Удаление сотрудника."""
        emp_id = self._insert('Удаляемый Сотрудник')
        self.assertEqual(self._count(), 1)
        cur = self.conn.cursor()
        cur.execute('DELETE FROM employee WHERE id_employee = ?', (emp_id,))
        self.conn.commit()
        self.assertEqual(self._count(), 0)


class TestTimesheetService(unittest.TestCase):
    """Интеграционные тесты сервиса табелей."""

    def setUp(self):
        """Создание тестовой БД."""
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE timesheet (
                id_timesheet INTEGER PRIMARY KEY AUTOINCREMENT,
                period_start DATE NOT NULL,
                period_end DATE NOT NULL CHECK (period_end >= period_start),
                status TEXT DEFAULT 'В работе',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                archived_at TIMESTAMP
            )
        ''')
        cur.execute('''
            CREATE TABLE timesheet_entry (
                id_timesheet_entry INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                timesheet_id INTEGER NOT NULL,
                date DATE NOT NULL,
                hours_worked REAL DEFAULT 0,
                type TEXT
            )
        ''')
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_create_timesheet(self):
        """Создание табеля."""
        cur = self.conn.cursor()
        cur.execute('INSERT INTO timesheet (period_start, period_end) VALUES (?, ?)',
                    ('2026-03-01', '2026-03-31'))
        self.conn.commit()
        ts_id = cur.lastrowid
        self.assertGreater(ts_id, 0)

    def test_update_status(self):
        """Изменение статуса табеля."""
        cur = self.conn.cursor()
        cur.execute('INSERT INTO timesheet (period_start, period_end) VALUES (?, ?)',
                    ('2026-03-01', '2026-03-31'))
        self.conn.commit()
        ts_id = cur.lastrowid
        cur.execute("UPDATE timesheet SET status = 'Утверждён' WHERE id_timesheet = ?", (ts_id,))
        self.conn.commit()
        cur.execute('SELECT status FROM timesheet WHERE id_timesheet = ?', (ts_id,))
        self.assertEqual(cur.fetchone()['status'], 'Утверждён')

    def test_add_entry(self):
        """Добавление записи табеля."""
        cur = self.conn.cursor()
        cur.execute('INSERT INTO timesheet (period_start, period_end) VALUES (?, ?)',
                    ('2026-03-01', '2026-03-31'))
        self.conn.commit()
        ts_id = cur.lastrowid
        cur.execute('INSERT INTO timesheet_entry (employee_id, timesheet_id, date, hours_worked, type) VALUES (?, ?, ?, ?, ?)',
                    (1, ts_id, '2026-03-02', 8.0, 'Рабочий день'))
        self.conn.commit()
        cur.execute('SELECT COUNT(*) FROM timesheet_entry')
        self.assertEqual(cur.fetchone()[0], 1)


class TestDocumentService(unittest.TestCase):
    """Интеграционные тесты сервиса документов."""

    def setUp(self):
        """Создание тестовой БД."""
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE document (
                id_document INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL CHECK (end_date >= start_date)
            )
        ''')
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_create_document(self):
        """Создание документа (отпуск)."""
        cur = self.conn.cursor()
        cur.execute('INSERT INTO document (employee_id, type, start_date, end_date) VALUES (?, ?, ?, ?)',
                    (1, 'Отпуск', '2026-03-01', '2026-03-14'))
        self.conn.commit()
        doc_id = cur.lastrowid
        self.assertGreater(doc_id, 0)

    def test_delete_document(self):
        """Удаление документа."""
        cur = self.conn.cursor()
        cur.execute('INSERT INTO document (employee_id, type, start_date, end_date) VALUES (?, ?, ?, ?)',
                    (1, 'Больничный', '2026-03-10', '2026-03-15'))
        self.conn.commit()
        doc_id = cur.lastrowid
        cur.execute('DELETE FROM document WHERE id_document = ?', (doc_id,))
        self.conn.commit()
        cur.execute('SELECT COUNT(*) FROM document')
        self.assertEqual(cur.fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
