"""
Вкладка управления сотрудниками на PyQt5.
ЛР1-Ф1: Ведение справочной информации о сотрудниках.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QPushButton, QLabel, QMessageBox, QAbstractItemView
)

from database.models import Employee
from services.employee_service import EmployeeService
from utils.validators import Validator
from ui.dialogs.employee_dialog import EmployeeDialog


class EmployeesTab(QWidget):
    """Вкладка сотрудников."""

    def __init__(self, db_manager, current_user, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.current_user = current_user
        self.service = EmployeeService(db_manager)
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Панель действий
        action_layout = QHBoxLayout()

        action_layout.addWidget(QLabel('Поиск:'))

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Поиск по ФИО или должности...')
        self.search_edit.textChanged.connect(self.search_employees)
        action_layout.addWidget(self.search_edit)

        self.add_btn = QPushButton('Добавить')
        self.add_btn.clicked.connect(self.add_employee)
        action_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton('Редактировать')
        self.edit_btn.clicked.connect(self.edit_employee)
        action_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton('Удалить')
        self.delete_btn.clicked.connect(self.delete_employee)
        action_layout.addWidget(self.delete_btn)

        layout.addLayout(action_layout)

        # Таблица сотрудников
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'ФИО', 'Должность', 'Ставка', 'Норма часов'])

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        self.table.cellDoubleClicked.connect(self.edit_employee)

        layout.addWidget(self.table)

        self.load_employees()

    def load_employees(self):
        """Загрузка списка сотрудников."""
        employees = self.service.get_all_employees()
        self.table.setRowCount(len(employees))

        for row_idx, emp in enumerate(employees):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(emp.id_employee)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(emp.fio))
            self.table.setItem(row_idx, 2, QTableWidgetItem(emp.position))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(emp.rate)))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(emp.norm_hours)))

    def search_employees(self):
        """Поиск сотрудников."""
        search_term = self.search_edit.text()
        self.table.setRowCount(0)

        if search_term:
            employees = self.service.search_employees(search_term)
        else:
            employees = self.service.get_all_employees()

        self.table.setRowCount(len(employees))
        for row_idx, emp in enumerate(employees):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(emp.id_employee)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(emp.fio))
            self.table.setItem(row_idx, 2, QTableWidgetItem(emp.position))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(emp.rate)))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(emp.norm_hours)))

    def get_selected_employee_id(self):
        """Получить ID выбранного сотрудника."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            item = self.table.item(row, 0)
            if item:
                return int(item.text())
        return None

    def add_employee(self):
        """Добавление сотрудника."""
        dialog = EmployeeDialog(self)
        if dialog.exec() == 1:
            employee = dialog.get_employee_data()
            is_valid, error = Validator.validate_employee_data(
                employee.fio, employee.position, employee.rate, employee.norm_hours
            )
            if is_valid:
                self.service.add_employee(employee)
                self.load_employees()
                QMessageBox.information(self, 'Успех', 'Сотрудник добавлен')
            else:
                QMessageBox.warning(self, 'Ошибка', error)

    def edit_employee(self):
        """Редактирование сотрудника."""
        employee_id = self.get_selected_employee_id()
        if not employee_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите сотрудника')
            return

        employee = self.service.get_employee_by_id(employee_id)
        if employee:
            dialog = EmployeeDialog(self, employee)
            if dialog.exec() == 1:
                updated_employee = dialog.get_employee_data()
                updated_employee.id_employee = employee_id
                is_valid, error = Validator.validate_employee_data(
                    updated_employee.fio, updated_employee.position,
                    updated_employee.rate, updated_employee.norm_hours
                )
                if is_valid:
                    self.service.update_employee(updated_employee)
                    self.load_employees()
                    QMessageBox.information(self, 'Успех', 'Данные обновлены')
                else:
                    QMessageBox.warning(self, 'Ошибка', error)

    def delete_employee(self):
        """Удаление сотрудника."""
        employee_id = self.get_selected_employee_id()
        if not employee_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите сотрудника')
            return

        reply = QMessageBox.question(
            self, 'Удаление',
            'Вы уверены, что хотите удалить этого сотрудника?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.service.delete_employee(employee_id)
            self.load_employees()
            QMessageBox.information(self, 'Успех', 'Сотрудник удалён')
