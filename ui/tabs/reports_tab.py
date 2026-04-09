"""
Вкладка формирования отчётов на PyQt5.
ЛР1-Ф4,Ф5: Генерация отчётов, выгрузка в XLSX.
"""

import os
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLabel, QComboBox, QMessageBox, QFileDialog, QAbstractItemView
)

from services.report_service import ReportService
from services.timesheet_service import TimesheetService


class ReportsTab(QWidget):
    """Вкладка отчётов."""

    def __init__(self, db_manager, current_user, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.current_user = current_user
        self.report_service = ReportService(db_manager)
        self.timesheet_service = TimesheetService(db_manager)
        self.current_timesheet_id = None
        self.timesheet_ids = []
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Панель действий
        action_layout = QHBoxLayout()

        action_layout.addWidget(QLabel('Выберите табель:'))

        self.timesheet_combo = QComboBox()
        self.load_timesheets()
        self.timesheet_combo.currentIndexChanged.connect(self.on_timesheet_changed)
        action_layout.addWidget(self.timesheet_combo)

        self.generate_btn = QPushButton('Сформировать отчёт')
        self.generate_btn.clicked.connect(self.generate_report)
        action_layout.addWidget(self.generate_btn)

        self.export_btn = QPushButton('Экспорт в XLSX')
        self.export_btn.clicked.connect(self.export_to_xlsx)
        action_layout.addWidget(self.export_btn)

        layout.addLayout(action_layout)

        # Таблица отчёта
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            '№', 'ФИО', 'Должность', 'Норма часов', 'Рабочие дни',
            'Отпуск', 'Больничный', 'Командировка', 'Неявка', 'Всего часов'
        ])

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        for col in range(3, 10):
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

    def load_timesheets(self):
        """Загрузка списка табелей."""
        self.timesheet_combo.blockSignals(True)
        self.timesheet_combo.clear()
        self.timesheet_ids = []

        timesheets = self.timesheet_service.get_all_timesheets()
        for ts in timesheets:
            display = f"{ts.period_start} — {ts.period_end} ({ts.status})"
            self.timesheet_combo.addItem(display)
            self.timesheet_ids.append(ts.id_timesheet)

        if self.timesheet_ids:
            self.current_timesheet_id = self.timesheet_ids[0]

        self.timesheet_combo.blockSignals(False)

    def on_timesheet_changed(self, index):
        """Обработка изменения выбранного табеля."""
        if index >= 0 and index < len(self.timesheet_ids):
            self.current_timesheet_id = self.timesheet_ids[index]

    def generate_report(self):
        """Формирование отчёта."""
        if not self.current_timesheet_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите табель')
            return

        report_data = self.report_service.get_timesheet_report(self.current_timesheet_id)

        self.table.setRowCount(len(report_data))

        for row_idx, data in enumerate(report_data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(data['fio']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(data['position']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(data['norm_hours'])))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(data['workdays'])))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(data['vacations'])))
            self.table.setItem(row_idx, 6, QTableWidgetItem(str(data['sick_leaves'])))
            self.table.setItem(row_idx, 7, QTableWidgetItem(str(data['business_trips'])))
            self.table.setItem(row_idx, 8, QTableWidgetItem(str(data['absences'])))
            self.table.setItem(row_idx, 9, QTableWidgetItem(f"{data['total_hours']:.2f}"))

        QMessageBox.information(self, 'Успех', f'Отчёт сформирован ({len(report_data)} сотрудников)')

    def export_to_xlsx(self):
        """Экспорт в XLSX."""
        if not self.current_timesheet_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите табель')
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Сохранить отчёт',
            f'tabel_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            'Excel Files (*.xlsx)'
        )

        if file_path:
            success = self.report_service.export_to_xlsx(self.current_timesheet_id, file_path)
            if success:
                QMessageBox.information(self, 'Успех', f'Отчёт экспортирован:\n{file_path}')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось экспортировать отчёт')
