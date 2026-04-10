"""
Диалог добавления/редактирования сотрудника на PyQt5.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, QPushButton, QMessageBox
)

from database.models import Employee


class EmployeeDialog(QDialog):
    """Диалог ввода/редактирования сотрудника."""

    def __init__(self, parent=None, employee: Employee = None):
        super().__init__(parent)
        self.employee = employee
        self.result = False
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        title = 'Редактирование сотрудника' if self.employee else 'Добавление сотрудника'
        self.setWindowTitle(title)
        self.setFixedSize(420, 280)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Форма
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.fio_edit = QLineEdit()
        self.fio_edit.setText(self.employee.fio if self.employee else '')
        self.fio_edit.setPlaceholderText('Введите ФИО')
        form_layout.addRow('ФИО:', self.fio_edit)

        self.position_edit = QLineEdit()
        self.position_edit.setText(self.employee.position if self.employee else '')
        self.position_edit.setPlaceholderText('Введите должность')
        form_layout.addRow('Должность:', self.position_edit)

        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0, 999.99)
        self.rate_spin.setSingleStep(0.25)
        self.rate_spin.setValue(self.employee.rate if self.employee else 1.0)
        form_layout.addRow('Ставка:', self.rate_spin)

        self.norm_hours_spin = QSpinBox()
        self.norm_hours_spin.setRange(0, 168)
        self.norm_hours_spin.setValue(self.employee.norm_hours if self.employee else 40)
        form_layout.addRow('Норма часов:', self.norm_hours_spin)

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

        self.fio_edit.setFocus()

    def save(self):
        """Сохранение данных."""
        self.result = True
        self.accept()

    def get_employee_data(self) -> Employee:
        """Получить данные сотрудника."""
        employee = Employee()
        employee.fio = self.fio_edit.text()
        employee.position = self.position_edit.text()
        employee.rate = self.rate_spin.value()
        employee.norm_hours = self.norm_hours_spin.value()
        return employee
