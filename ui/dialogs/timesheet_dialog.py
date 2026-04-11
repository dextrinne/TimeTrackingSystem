"""
Диалог создания табеля на PyQt5.
"""

from datetime import date, datetime

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QDateEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate

from utils.validators import Validator


class TimesheetDialog(QDialog):
    """Диалог создания табеля."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result = False
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle('Создание табеля')
        self.setFixedSize(380, 220)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Форма
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Расчёт предыдущего месяца (корректная обработка января)
        today = date.today()
        if today.month == 1:
            prev_month_start = date(today.year - 1, 12, 1)
        else:
            prev_month_start = date(today.year, today.month - 1, 1)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate(prev_month_start.year, prev_month_start.month, prev_month_start.day))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat('yyyy-MM-dd')
        form_layout.addRow('Дата начала:', self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat('yyyy-MM-dd')
        form_layout.addRow('Дата окончания:', self.end_date_edit)

        layout.addLayout(form_layout)

        # Кнопки
        button_layout = QHBoxLayout()

        self.create_btn = QPushButton('Создать')
        self.create_btn.clicked.connect(self.create)

        self.cancel_btn = QPushButton('Отмена')
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def create(self):
        """Валидация и создание табеля."""
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()

        is_valid, error = Validator.validate_dates(start_date, end_date)
        if not is_valid:
            QMessageBox.warning(self, 'Ошибка', error)
            return

        self.result = True
        self.accept()

    def get_period(self):
        """Получить период табеля."""
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        return start_date, end_date
