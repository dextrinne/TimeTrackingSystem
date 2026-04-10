"""
Диалог документа на PyQt5.
"""

from datetime import date, datetime

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QDateEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate

from database.models import Document
from utils.validators import Validator


class DocumentDialog(QDialog):
    """Диалог ввода/редактирования документа."""

    def __init__(self, parent=None, employee_service=None, document: Document = None):
        super().__init__(parent)
        self.employee_service = employee_service
        self.document = document
        self.result = False
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        title = 'Редактирование документа' if self.document else 'Добавление документа'
        self.setWindowTitle(title)
        self.setFixedSize(420, 300)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Форма
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Выбор сотрудника
        self.employee_combo = QComboBox()
        employees = self.employee_service.get_all_employees() if self.employee_service else []
        self.employee_map = {}
        for emp in employees:
            self.employee_combo.addItem(emp.fio, emp.id_employee)
            self.employee_map[emp.id_employee] = emp.fio

        if self.document and self.document.employee_id in self.employee_map:
            index = self.employee_combo.findData(self.document.employee_id)
            if index >= 0:
                self.employee_combo.setCurrentIndex(index)

        form_layout.addRow('Сотрудник:', self.employee_combo)

        # Тип документа
        self.type_combo = QComboBox()
        doc_types = ['Отпуск', 'Больничный', 'Командировка', 'Отгул']
        self.type_combo.addItems(doc_types)

        if self.document:
            index = self.type_combo.findText(self.document.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)

        form_layout.addRow('Тип документа:', self.type_combo)

        # Даты
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.today())
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat('yyyy-MM-dd')
        if self.document:
            self.start_date_edit.setDate(
                QDate(self.document.start_date.year, self.document.start_date.month, self.document.start_date.day)
            )
        form_layout.addRow('Дата начала:', self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.today())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat('yyyy-MM-dd')
        if self.document:
            self.end_date_edit.setDate(
                QDate(self.document.end_date.year, self.document.end_date.month, self.document.end_date.day)
            )
        form_layout.addRow('Дата окончания:', self.end_date_edit)

        layout.addLayout(form_layout)

        # Кнопки
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton('Сохранить')
        self.save_btn.clicked.connect(self.save)

        self.cancel_btn = QPushButton('Отмена')
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def save(self):
        """Сохранение данных с валидацией."""
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()

        is_valid, error = Validator.validate_dates(start_date, end_date)
        if not is_valid:
            QMessageBox.warning(self, 'Ошибка', error)
            return

        doc_type = self.type_combo.currentText()
        is_valid, error = Validator.validate_document_type(doc_type)
        if not is_valid:
            QMessageBox.warning(self, 'Ошибка', error)
            return

        self.result = True
        self.accept()

    def get_document_data(self) -> Document:
        """Получить данные документа."""
        document = Document()
        document.employee_id = self.employee_combo.currentData() or 0
        document.type = self.type_combo.currentText()
        document.start_date = self.start_date_edit.date().toPyDate()
        document.end_date = self.end_date_edit.date().toPyDate()
        return document
