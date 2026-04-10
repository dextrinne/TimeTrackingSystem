"""
Вкладка управления табелями на PyQt5.
ЛР1-Ф3: Формирование электронного табеля.
ЛР2: Автоматический расчёт, управление статусами.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLabel, QComboBox, QMessageBox, QGroupBox,
    QAbstractItemView
)

from database.models import Timesheet, TimesheetEntry
from services.timesheet_service import TimesheetService
from services.employee_service import EmployeeService
from ui.dialogs.timesheet_dialog import TimesheetDialog


class TimesheetsTab(QWidget):
    """Вкладка табелей."""

    def __init__(self, db_manager, current_user, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.current_user = current_user
        self.timesheet_service = TimesheetService(db_manager)
        self.employee_service = EmployeeService(db_manager)
        self.current_timesheet_id = None
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Панель действий
        action_layout = QHBoxLayout()

        self.create_btn = QPushButton('Создать табель')
        self.create_btn.clicked.connect(self.create_timesheet)
        action_layout.addWidget(self.create_btn)

        self.delete_btn = QPushButton('Удалить табель')
        self.delete_btn.clicked.connect(self.delete_timesheet)
        action_layout.addWidget(self.delete_btn)

        action_layout.addWidget(QLabel('Статус:'))

        self.status_combo = QComboBox()
        self.status_combo.addItems(['В работе', 'Утверждён', 'Архивирован'])
        self.status_combo.currentTextChanged.connect(self.change_status)
        action_layout.addWidget(self.status_combo)

        self.generate_btn = QPushButton('Сформировать дни')
        self.generate_btn.clicked.connect(self.generate_days)
        action_layout.addWidget(self.generate_btn)

        self.totals_btn = QPushButton('Подсчитать итоги')
        self.totals_btn.clicked.connect(self.calculate_totals)
        action_layout.addWidget(self.totals_btn)

        layout.addLayout(action_layout)

        # Список табелей
        timesheet_group = QGroupBox('Табели')
        timesheet_layout = QVBoxLayout(timesheet_group)

        self.timesheet_table = QTableWidget()
        self.timesheet_table.setColumnCount(4)
        self.timesheet_table.setHorizontalHeaderLabels(['ID', 'Период', 'Статус', 'Создан'])

        self.timesheet_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.timesheet_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.timesheet_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.timesheet_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.timesheet_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.timesheet_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.timesheet_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.timesheet_table.setAlternatingRowColors(True)
        self.timesheet_table.setMaximumHeight(150)

        self.timesheet_table.selectionModel().selectionChanged.connect(self.on_timesheet_selected)

        timesheet_layout.addWidget(self.timesheet_table)
        layout.addWidget(timesheet_group)

        # Записи табеля
        entries_group = QGroupBox('Записи табеля')
        entries_layout = QVBoxLayout(entries_group)

        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(5)
        self.entries_table.setHorizontalHeaderLabels(['ID', 'Сотрудник ID', 'Дата', 'Часы', 'Тип'])

        self.entries_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.entries_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.entries_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.entries_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.entries_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.entries_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.entries_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.entries_table.setAlternatingRowColors(True)

        entries_layout.addWidget(self.entries_table)
        layout.addWidget(entries_group)

        self.load_timesheets()

    def load_timesheets(self):
        """Загрузка списка табелей."""
        timesheets = self.timesheet_service.get_all_timesheets()
        self.timesheet_table.setRowCount(len(timesheets))

        for row_idx, ts in enumerate(timesheets):
            self.timesheet_table.setItem(row_idx, 0, QTableWidgetItem(str(ts.id_timesheet)))
            self.timesheet_table.setItem(row_idx, 1, QTableWidgetItem(f"{ts.period_start} — {ts.period_end}"))
            self.timesheet_table.setItem(row_idx, 2, QTableWidgetItem(ts.status))
            self.timesheet_table.setItem(row_idx, 3, QTableWidgetItem(str(ts.created_at)))

    def on_timesheet_selected(self, selected, deselected):
        """Обработка выбора табеля."""
        selected_rows = self.timesheet_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            id_item = self.timesheet_table.item(row, 0)
            status_item = self.timesheet_table.item(row, 2)
            if id_item and status_item:
                self.current_timesheet_id = int(id_item.text())
                self.status_combo.blockSignals(True)
                self.status_combo.setCurrentText(status_item.text())
                self.status_combo.blockSignals(False)
                self.load_entries()

    def load_entries(self):
        """Загрузка записей выбранного табеля."""
        if not self.current_timesheet_id:
            return

        entries = self.timesheet_service.get_entries_by_timesheet(self.current_timesheet_id)
        self.entries_table.setRowCount(len(entries))

        for row_idx, entry in enumerate(entries):
            self.entries_table.setItem(row_idx, 0, QTableWidgetItem(str(entry.id_timesheet_entry)))
            self.entries_table.setItem(row_idx, 1, QTableWidgetItem(str(entry.employee_id)))
            self.entries_table.setItem(row_idx, 2, QTableWidgetItem(str(entry.date)))
            self.entries_table.setItem(row_idx, 3, QTableWidgetItem(str(entry.hours_worked)))
            self.entries_table.setItem(row_idx, 4, QTableWidgetItem(entry.type))

    def create_timesheet(self):
        """Создание нового табеля."""
        dialog = TimesheetDialog(self)
        if dialog.exec() == 1:
            period_start, period_end = dialog.get_period()
            timesheet_id = self.timesheet_service.create_timesheet(period_start, period_end)
            if timesheet_id:
                self.load_timesheets()
                QMessageBox.information(self, 'Успех', 'Табель создан')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось создать табель')

    def change_status(self):
        """Изменение статуса табеля."""
        if not self.current_timesheet_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите табель')
            return

        status = self.status_combo.currentText()
        self.timesheet_service.update_timesheet_status(self.current_timesheet_id, status)
        self.load_timesheets()
        QMessageBox.information(self, 'Успех', f'Статус изменён на "{status}"')

    def generate_days(self):
        """Автоматическое формирование дней."""
        if not self.current_timesheet_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите табель')
            return

        employees = self.employee_service.get_all_employees()
        if not employees:
            QMessageBox.warning(self, 'Ошибка', 'Нет сотрудников в базе')
            return

        employee_ids = [emp.id_employee for emp in employees]
        self.timesheet_service.generate_timesheet_structure(self.current_timesheet_id, employee_ids)
        self.load_entries()
        QMessageBox.information(self, 'Успех', 'Структура табеля сформирована')

    def calculate_totals(self):
        """Подсчёт итогов."""
        if not self.current_timesheet_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите табель')
            return

        employees = self.employee_service.get_all_employees()
        totals_text = "ИТОГИ ПО ТАБЕЛЯМ:\n\n"

        for emp in employees:
            totals = self.timesheet_service.calculate_employee_totals(emp.id_employee, self.current_timesheet_id)
            totals_text += f"{emp.fio}:\n"
            totals_text += f"  Рабочих дней: {totals['workdays']}\n"
            totals_text += f"  Всего часов: {totals['total_hours']}\n"
            totals_text += f"  Отпуск: {totals['vacations']} дн.\n"
            totals_text += f"  Больничный: {totals['sick_leaves']} дн.\n\n"

        QMessageBox.information(self, 'Итоги', totals_text)

    def delete_timesheet(self):
        """Удаление выбранного табеля."""
        if not self.current_timesheet_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите табель для удаления')
            return

        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            'Вы уверены, что хотите удалить этот табель?\nВсе записи табеля будут удалены.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = self.timesheet_service.delete_timesheet(self.current_timesheet_id)
            if success:
                self.current_timesheet_id = None
                self.load_timesheets()
                self.entries_table.setRowCount(0)
                QMessageBox.information(self, 'Успех', 'Табель удалён')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось удалить табель')
