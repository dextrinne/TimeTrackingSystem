"""
Сервис управления табелями.
ЛР1-Ф3: Формирование электронного табеля.
ЛР2: Автоматический расчёт, управление статусами.
"""

import sys
import os
from datetime import datetime, date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from database.models import Timesheet, TimesheetEntry, DayType


class TimesheetService:
    """Сервис для CRUD операций с табелями."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_all_timesheets(self):
        """Получить все табели."""
        rows = self.db.execute_query(
            """SELECT id_timesheet, period_start, period_end, status, 
                      created_at, approved_at, archived_at 
               FROM timesheet 
               ORDER BY period_start DESC""",
            fetch=True
        )
        return [Timesheet.from_row(row) for row in rows] if rows else []

    def get_timesheet_by_id(self, timesheet_id):
        """Получить табель по ID."""
        row = self.db.execute_query(
            """SELECT id_timesheet, period_start, period_end, status, 
                      created_at, approved_at, archived_at 
               FROM timesheet WHERE id_timesheet = %s""",
            (timesheet_id,),
            fetchone=True
        )
        return Timesheet.from_row(row) if row else None

    def create_timesheet(self, period_start, period_end, status="В работе"):
        """Создать новый табель за период."""
        row = self.db.execute_query(
            """INSERT INTO timesheet (period_start, period_end, status) 
               VALUES (%s, %s, %s) 
               RETURNING id_timesheet""",
            (period_start, period_end, status),
            fetchone=True
        )
        return row[0] if row else None

    def update_timesheet_status(self, timesheet_id, status):
        """Обновить статус табеля."""
        now = datetime.now()
        if status == "Утверждён":
            self.db.execute_query(
                """UPDATE timesheet SET status = %s, approved_at = %s WHERE id_timesheet = %s""",
                (status, now, timesheet_id)
            )
        elif status == "Архивирован":
            self.db.execute_query(
                """UPDATE timesheet SET status = %s, archived_at = %s WHERE id_timesheet = %s""",
                (status, now, timesheet_id)
            )
        else:
            self.db.execute_query(
                """UPDATE timesheet SET status = %s WHERE id_timesheet = %s""",
                (status, timesheet_id)
            )

    def delete_timesheet(self, timesheet_id):
        """Удалить табель и все его записи."""
        self.db.execute_query(
            "DELETE FROM timesheet_entry WHERE timesheet_id = %s",
            (timesheet_id,)
        )
        self.db.execute_query(
            "DELETE FROM timesheet WHERE id_timesheet = %s",
            (timesheet_id,)
        )

    def add_entry(self, entry: TimesheetEntry):
        """Добавить запись в табель."""
        self.db.execute_query(
            """INSERT INTO timesheet_entry (employee_id, timesheet_id, date, hours_worked, type) 
               VALUES (%s, %s, %s, %s, %s)""",
            (entry.employee_id, entry.timesheet_id, entry.date, 
             entry.hours_worked, entry.type)
        )

    def update_entry(self, entry: TimesheetEntry):
        """Обновить запись в табеле."""
        self.db.execute_query(
            """UPDATE timesheet_entry 
               SET hours_worked = %s, type = %s 
               WHERE id_timesheet_entry = %s""",
            (entry.hours_worked, entry.type, entry.id_timesheet_entry)
        )

    def get_entries_by_timesheet(self, timesheet_id):
        """Получить все записи табеля."""
        rows = self.db.execute_query(
            """SELECT id_timesheet_entry, employee_id, timesheet_id, date, 
                      hours_worked, type 
               FROM timesheet_entry 
               WHERE timesheet_id = %s 
               ORDER BY employee_id, date""",
            (timesheet_id,),
            fetch=True
        )
        return [TimesheetEntry.from_row(row) for row in rows] if rows else []

    def get_entries_by_employee_and_timesheet(self, employee_id, timesheet_id):
        """Получить записи табеля для конкретного сотрудника."""
        rows = self.db.execute_query(
            """SELECT id_timesheet_entry, employee_id, timesheet_id, date, 
                      hours_worked, type 
               FROM timesheet_entry 
               WHERE employee_id = %s AND timesheet_id = %s 
               ORDER BY date""",
            (employee_id, timesheet_id),
            fetch=True
        )
        return [TimesheetEntry.from_row(row) for row in rows] if rows else []

    def generate_timesheet_structure(self, timesheet_id, employee_ids):
        """Автоматически сформировать структуру табеля рабочими днями.
        
        ЛР2: Автоматическое формирование структуры табеля.
        """
        timesheet = self.get_timesheet_by_id(timesheet_id)
        if not timesheet:
            return

        current_date = timesheet.period_start
        while current_date <= timesheet.period_end:
            # Пропускаем выходные (суббота=5, воскресенье=6)
            if current_date.weekday() < 5:
                for emp_id in employee_ids:
                    # Проверяем, нет ли уже записи
                    existing = self.db.execute_query(
                        """SELECT id_timesheet_entry FROM timesheet_entry 
                           WHERE employee_id = %s AND timesheet_id = %s AND date = %s""",
                        (emp_id, timesheet_id, current_date),
                        fetchone=True
                    )
                    if not existing:
                        self.db.execute_query(
                            """INSERT INTO timesheet_entry (employee_id, timesheet_id, date, hours_worked, type) 
                               VALUES (%s, %s, %s, 0, 'Рабочий день')""",
                            (emp_id, timesheet_id, current_date)
                        )
            current_date += timedelta(days=1)

    def calculate_employee_totals(self, employee_id, timesheet_id):
        """Подсчёт итогов по сотруднику в табеле.
        
        ЛР2: Автоматический подсчёт итогов.
        
        Returns:
            dict: total_days, total_hours, workdays, vacations, sick_leaves, business_trips
        """
        rows = self.db.execute_query(
            """SELECT type, COUNT(*) as days, COALESCE(SUM(hours_worked), 0) as hours
               FROM timesheet_entry 
               WHERE employee_id = %s AND timesheet_id = %s
               GROUP BY type""",
            (employee_id, timesheet_id),
            fetch=True
        )

        totals = {
            'total_days': 0,
            'total_hours': 0.0,
            'workdays': 0,
            'vacations': 0,
            'sick_leaves': 0,
            'business_trips': 0,
            'absences': 0
        }

        if rows:
            for row in rows:
                day_type, days, hours = row
                totals['total_days'] += days
                totals['total_hours'] += float(hours)
                
                if day_type == 'Рабочий день':
                    totals['workdays'] = days
                elif day_type == 'Отпуск':
                    totals['vacations'] = days
                elif day_type == 'Больничный':
                    totals['sick_leaves'] = days
                elif day_type == 'Командировка':
                    totals['business_trips'] = days
                elif day_type == 'Неявка':
                    totals['absences'] = days

        return totals
