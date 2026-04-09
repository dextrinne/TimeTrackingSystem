"""
Сервис управления документами.
ЛР1-Ф2: Ввод плановых неявок.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from database.models import Document


class DocumentService:
    """Сервис для CRUD операций с документами."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_all_documents(self):
        """Получить все документы."""
        rows = self.db.execute_query(
            """SELECT id_document, employee_id, type, start_date, end_date 
               FROM document 
               ORDER BY start_date DESC""",
            fetch=True
        )
        return [Document.from_row(row) for row in rows] if rows else []

    def get_documents_by_employee(self, employee_id):
        """Получить документы конкретного сотрудника."""
        rows = self.db.execute_query(
            """SELECT id_document, employee_id, type, start_date, end_date 
               FROM document 
               WHERE employee_id = %s 
               ORDER BY start_date DESC""",
            (employee_id,),
            fetch=True
        )
        return [Document.from_row(row) for row in rows] if rows else []

    def add_document(self, document: Document):
        """Добавить новый документ."""
        self.db.execute_query(
            """INSERT INTO document (employee_id, type, start_date, end_date) 
               VALUES (%s, %s, %s, %s)""",
            (document.employee_id, document.type, 
             document.start_date, document.end_date)
        )

    def update_document(self, document: Document):
        """Обновить документ."""
        self.db.execute_query(
            """UPDATE document 
               SET type = %s, start_date = %s, end_date = %s 
               WHERE id_document = %s""",
            (document.type, document.start_date, 
             document.end_date, document.id_document)
        )

    def delete_document(self, document_id):
        """Удалить документ."""
        self.db.execute_query(
            "DELETE FROM document WHERE id_document = %s",
            (document_id,)
        )

    def get_documents_in_period(self, start_date, end_date):
        """Получить документы, пересекающие период."""
        rows = self.db.execute_query(
            """SELECT id_document, employee_id, type, start_date, end_date 
               FROM document 
               WHERE start_date <= %s AND end_date >= %s
               ORDER BY start_date""",
            (end_date, start_date),
            fetch=True
        )
        return [Document.from_row(row) for row in rows] if rows else []

    def is_employee_absent(self, employee_id, date):
        """Проверить, отсутствует ли сотрудник в указанную дату.
        
        Returns:
            tuple: (is_absent: bool, document_type: str or None)
        """
        row = self.db.execute_query(
            """SELECT type FROM document 
               WHERE employee_id = %s AND start_date <= %s AND end_date >= %s
               LIMIT 1""",
            (employee_id, date, date),
            fetchone=True
        )
        if row:
            return True, row[0]
        return False, None
