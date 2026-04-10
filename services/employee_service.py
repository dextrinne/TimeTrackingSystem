"""
Сервис управления сотрудниками.
ЛР1-Ф1: Ведение справочной информации о сотрудниках.
"""

from database.db_manager import DatabaseManager
from database.models import Employee


class EmployeeService:
    """Сервис для CRUD операций с сотрудниками."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_all_employees(self):
        """Получить всех сотрудников."""
        rows = self.db.execute_query(
            "SELECT id_employee, fio, position, rate, norm_hours FROM employee ORDER BY fio",
            fetch=True
        )
        return [Employee.from_row(row) for row in rows] if rows else []

    def get_employee_by_id(self, employee_id):
        """Получить сотрудника по ID."""
        row = self.db.execute_query(
            "SELECT id_employee, fio, position, rate, norm_hours FROM employee WHERE id_employee = %s",
            (employee_id,),
            fetchone=True
        )
        return Employee.from_row(row) if row else None

    def add_employee(self, employee: Employee):
        """Добавить нового сотрудника."""
        self.db.execute_query(
            """INSERT INTO employee (fio, position, rate, norm_hours) 
               VALUES (%s, %s, %s, %s)""",
            (employee.fio, employee.position, employee.rate, employee.norm_hours)
        )

    def update_employee(self, employee: Employee):
        """Обновить данные сотрудника."""
        self.db.execute_query(
            """UPDATE employee 
               SET fio = %s, position = %s, rate = %s, norm_hours = %s 
               WHERE id_employee = %s""",
            (employee.fio, employee.position, employee.rate, 
             employee.norm_hours, employee.id_employee)
        )

    def delete_employee(self, employee_id):
        """Удалить сотрудника."""
        self.db.execute_query(
            "DELETE FROM employee WHERE id_employee = %s",
            (employee_id,)
        )

    def search_employees(self, search_term):
        """Поиск сотрудников по ФИО или должности."""
        rows = self.db.execute_query(
            """SELECT id_employee, fio, position, rate, norm_hours 
               FROM employee 
               WHERE fio ILIKE %s OR position ILIKE %s
               ORDER BY fio""",
            (f"%{search_term}%", f"%{search_term}%"),
            fetch=True
        )
        return [Employee.from_row(row) for row in rows] if rows else []
