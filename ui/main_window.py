from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QPushButton, QLabel, QComboBox,
                             QSpinBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QFrame, QScrollArea,
                             QToolTip, QTreeWidget, QTreeWidgetItem, QMenu,
                             QToolBar, QStatusBar, QApplication, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QIcon, QFont, QAction, QKeySequence, QColor, QBrush

QApplication.setStyle("Fusion")
QApplication.setPalette(QApplication.style().standardPalette())

# Отключаем всплывающие подсказки во всем приложении
QToolTip.setFont(QFont())

import os
import json
from datetime import datetime
import calendar

from frontend.styles import DayTypes, AppStyle
from frontend.config import AppConfig, UIConfig
from ui.widgets import CalendarTableWidget, EmployeeInfoCard
from ui.dialogs import EmployeeDialog, DayTypeMenuDialog, ExportDialog

# ----------------------------------------------------------------------------------------------------------

class MainWindow(QMainWindow):
  
    # Сигналы
    month_changed = pyqtSignal(int, int)  # month, year
    employee_added = pyqtSignal(dict)
    employee_edited = pyqtSignal(int, dict)
    employee_deleted = pyqtSignal(int)
    day_type_changed = pyqtSignal(tuple, object)  # (emp_idx, day), data (dict or str)
    
    def __init__(self, app_controller):
        super().__init__()
        self.app = app_controller
        self.current_month = AppConfig.DEFAULT_MONTH
        self.current_year = AppConfig.DEFAULT_YEAR
        self.employees = []
        self.day_data = {}
        
        self.setup_ui()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_connections()
    
    # Настройка пользовательского интерфейса
    def setup_ui(self):
        self.setWindowTitle(AppConfig.APP_TITLE)
        self.setMinimumSize(*AppConfig.MIN_WINDOW_SIZE)
        self.resize(*AppConfig.WINDOW_SIZE)
        
        # Применение стилей
        self.setStyleSheet(AppStyle.get_stylesheet())
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        # Верхняя панель с информацией
        self.setup_info_panel(main_layout)
        
        # Создание вкладок
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Вкладка Табель
        self.timetable_tab = QWidget()
        self.setup_timetable_tab()
        self.tab_widget.addTab(self.timetable_tab, "Табель")
        
        # Вкладка Сотрудники
        self.employees_tab = QWidget()
        self.setup_employees_tab()
        self.tab_widget.addTab(self.employees_tab, "Сотрудники")
        
        # Вкладка Архив
        self.archive_tab = QWidget()
        self.setup_archive_tab()
        self.tab_widget.addTab(self.archive_tab, "Архив")
        
        main_layout.addWidget(self.tab_widget)
    

# ----------------------------------------------------------------------------------------------------------

    def setup_info_panel(self, parent_layout):
        info_frame = QFrame()
        info_frame.setMaximumHeight(80)
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #E1ECF7;
                padding: 10px;
            }}
        """)
        
        info_layout = QHBoxLayout()
        info_frame.setLayout(info_layout)
        
        # Заголовок
        title_label = QLabel("ТАБЕЛЬ УЧЁТА РАБОЧЕГО ВРЕМЕНИ")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: #83B0E1;")
        info_layout.addWidget(title_label)
        
        info_layout.addStretch()
        info_layout.addStretch()
        
        # Инструкция
        instruction_label = QLabel("Нажмите дважды ЛЕВОЙ кнопкой мыши для ввода часов   |   ПРАВОЙ, чтобы выбрать тип")
        instruction_label.setStyleSheet(f"color: #71A5DE; font-style: italic;")
        info_layout.addWidget(instruction_label)
        
        parent_layout.addWidget(info_frame)
    
    
# ----------------------------------------------------------------------------------------------------------

    def setup_toolbar(self):
        toolbar = QToolBar("Основная панель")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Создаем кастомные кнопки для тулбара
        from PyQt6.QtWidgets import QToolButton
        
        # Экспорт
        export_btn = QToolButton()
        export_btn.setText("ЭКСПОРТ")
        export_btn.setStyleSheet("""
            QToolButton {
                color: white;
                font-weight: bold;
                padding: 6px 15px;
                border-radius: 4px;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: #5A95CC;
            }
            QToolButton:pressed {
                background-color: #4A86C8;
            }
        """)
        export_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        export_btn.clicked.connect(self.export_to_excel)
        export_btn.setToolTip("")  # Заглушка
        toolbar.addWidget(export_btn)
        
        toolbar.addSeparator()
        
        # Отмена
        undo_btn = QToolButton()
        undo_btn.setText("ОТМЕНИТЬ")
        undo_btn.setStyleSheet("""
            QToolButton {
                color: white;
                font-weight: bold;
                padding: 6px 15px;
                border-radius: 4px;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: #5A95CC;
            }
            QToolButton:pressed {
                background-color: #4A86C8;
            }
        """)
        undo_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        undo_btn.clicked.connect(self.app.undo_last_action)
        undo_btn.setToolTip("")  # Заглушка
        toolbar.addWidget(undo_btn)
        
        # Добавляем растяжение
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
        
        # Выбор месяца и года
        month_label = QLabel("Месяц:")
        month_label.setStyleSheet("margin-left: 10px; font-weight: bold; color: #F8F9FB;")
        toolbar.addWidget(month_label)
        
        self.month_combo = QComboBox()
        self.month_combo.addItems(AppConfig.MONTHS)
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.month_combo.setMinimumWidth(120)
        toolbar.addWidget(self.month_combo)
        
        year_label = QLabel("Год:")
        year_label.setStyleSheet("margin-left: 10px; font-weight: bold; color: #F8F9FB;")
        toolbar.addWidget(year_label)
        
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2130)
        self.year_spin.setValue(self.current_year)
        self.year_spin.setMinimumWidth(80)
        toolbar.addWidget(self.year_spin)

    def setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.status_label = QLabel("Готов к работе")
        self.statusbar.addWidget(self.status_label)
        
        # Автосохранение
        self.autosave_label = QLabel("Автосохранение включено")
        self.autosave_label.setStyleSheet(f"color: #50C878; margin-right: 10px; font-weight: bold;")
        self.statusbar.addPermanentWidget(self.autosave_label)
    
# ----------------------------------------------------------------------------------------------------------

    def setup_timetable_tab(self):
        layout = QVBoxLayout()
        self.timetable_tab.setLayout(layout)
        
        # Создание области прокрутки для календаря
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        # Виджет календаря
        self.calendar_widget = QWidget()
        self.calendar_layout = QVBoxLayout()
        self.calendar_widget.setLayout(self.calendar_layout)
        
        # Таблица календаря
        self.calendar_table = CalendarTableWidget()
        self.calendar_layout.addWidget(self.calendar_table)
        
        scroll_area.setWidget(self.calendar_widget)
        layout.addWidget(scroll_area)
    

    # Вкладка с сотрудниками
    def setup_employees_tab(self):
        layout = QVBoxLayout()
        self.employees_tab.setLayout(layout)
        
        # Панель инструментов
        toolbar = QHBoxLayout()
        
        add_button = QPushButton("Добавить сотрудника")
        add_button.clicked.connect(self.add_employee)
        toolbar.addWidget(add_button)
        
        edit_button = QPushButton( "Редактировать")
        edit_button.clicked.connect(self.edit_employee)
        toolbar.addWidget(edit_button)
        
        delete_button = QPushButton("Удалить")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        delete_button.clicked.connect(self.delete_employee)
        toolbar.addWidget(delete_button)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Таблица сотрудников
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(8)
        self.employees_table.setHorizontalHeaderLabels([
            "ФИО", "Должность", "Ставка", "Рабочие дни", 
            "Выходные", "Отпуск", "Больничный", "Прочее"
        ])
        
        # Запрет редактирования
        self.employees_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Настройка таблицы
        self.employees_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.employees_table.setAlternatingRowColors(True)
        self.employees_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.employees_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        layout.addWidget(self.employees_table)
    

    # Настройка вкладки архива
    def setup_archive_tab(self):
        layout = QVBoxLayout()
        self.archive_tab.setLayout(layout)
        
        # Панель инструментов
        toolbar = QHBoxLayout()
        
        save_button = QPushButton("Сохранить текущий табель")
        save_button.clicked.connect(self.app.save_current_to_archive)
        toolbar.addWidget(save_button)
        
        load_button = QPushButton("Загрузить")
        load_button.clicked.connect(self.app.load_selected_from_archive)
        toolbar.addWidget(load_button)
        
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.app.delete_selected_from_archive)
        toolbar.addWidget(delete_button)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Дерево архива
        self.archive_tree = QTreeWidget()
        self.archive_tree.setHeaderLabels(["Месяц", "Год", "Дата сохранения", "Файл"])
        self.archive_tree.setAlternatingRowColors(True)
        
        # Запрет редактирования
        self.archive_tree.setEditTriggers(QTreeWidget.EditTrigger.NoEditTriggers)   

        # Настройка ширины колонок
        self.archive_tree.setColumnWidth(0, 150)
        self.archive_tree.setColumnWidth(1, 100)
        self.archive_tree.setColumnWidth(2, 200)
        self.archive_tree.setColumnWidth(3, 200)
        
        layout.addWidget(self.archive_tree)
    
# ----------------------------------------------------------------------------------------------------------

    # Настройка соединений сигналов и слотов
    def setup_connections(self):
        # Соединения для контролов месяца/года
        self.month_combo.currentIndexChanged.connect(self.on_month_changed)
        self.year_spin.valueChanged.connect(self.on_year_changed)
    
    # Обработчик изменения месяца
    def on_month_changed(self, index):
        self.current_month = index + 1
        self.month_changed.emit(self.current_month, self.current_year)
    
    # Обработчик изменения года
    def on_year_changed(self, year):
        self.current_year = year
        self.month_changed.emit(self.current_month, self.current_year)
    
    # Обработчик левого клика
    def on_day_left_click(self, day_key):
        pass
    
    # Обработчик изменения часов в ячейке
    def on_day_hours_changed(self, day_key, hours):
        emp_idx, day = day_key
        cell_data = self.day_data.get(day_key, {'code': DayTypes.EMPTY, 'hours': 0})
        
        if isinstance(cell_data, str):
            current_code = cell_data if cell_data else DayTypes.EMPTY
        else:
            current_code = cell_data.get('code', DayTypes.EMPTY)
        
        if not current_code or not current_code.strip():
            current_code = DayTypes.EMPTY
        
        if hours > 0:
            self.day_type_changed.emit(day_key, {'code': DayTypes.WORKDAY, 'hours': hours})
        else:
            self.day_type_changed.emit(day_key, {'code': current_code, 'hours': 0})
    
    # Обработчик правого клика - выбор типа дня через контекстное меню
    def on_day_right_click(self, day_key):
        emp_idx, day = day_key
        
        # Получаем текущие данные ячейки
        cell_data = self.day_data.get(day_key, {'code': DayTypes.EMPTY, 'hours': 0})
        current_code = cell_data if isinstance(cell_data, str) else cell_data.get('code', DayTypes.EMPTY)
        current_hours = 0 if isinstance(cell_data, str) else cell_data.get('hours', 0)
        
        # Создаем и показываем контекстное меню
        from ui.dialogs import DayTypeContextMenu
        
        context_menu = DayTypeContextMenu(self)
        
        # Получаем позицию курсора для отображения меню
        cursor_pos = self.cursor().pos()
        
        # Подключаем сигнал выбора типа
        def on_type_selected(code):
            # Для нерабочих дней часы = 0, для рабочих оставляем текущие
            hours = current_hours if code == DayTypes.WORKDAY else 0
            self.day_type_changed.emit(day_key, {'code': code, 'hours': hours})
        
        context_menu.type_selected.connect(on_type_selected)
        context_menu.exec(cursor_pos)
   
    # Обновление календаря
    def update_calendar(self, year, month, employees, day_data):
        self.current_year = year
        self.current_month = month
        self.employees = employees
        self.day_data = day_data

        # Обновление контролов
        self.month_combo.blockSignals(True)
        self.year_spin.blockSignals(True)
        self.month_combo.setCurrentIndex(month - 1)
        self.year_spin.setValue(year)
        self.month_combo.blockSignals(False)
        self.year_spin.blockSignals(False)
        
        # Пересоздание календаря
        self.calendar_table.clear_calendar()
        self.calendar_table.create_calendar(year, month, employees, day_data)
        
        for row in range(self.calendar_table.rowCount()):
            # Колонка 0 - ФИО
            name_item = self.calendar_table.item(row, 0)
            if name_item:
                name_item.setForeground(QBrush(QColor("#2C3E50")))

        # Переподключение сигналов
        for day_key, cell_widget in self.calendar_table.day_cells.items():
            cell_widget.clicked_left.connect(self.on_day_left_click)
            cell_widget.clicked_right.connect(self.on_day_right_click)
            cell_widget.hours_changed.connect(self.on_day_hours_changed)  # Новый сигнал

        # Обновление статуса
        self.status_label.setText(f"Отображен табель за {AppConfig.MONTHS[month-1]} {year} года")
    
    # Обновление ячейки дня
    def update_day_cell(self, emp_idx, day, data):
        if isinstance(data, str):
            # Для обратной совместимости
            code = data
            hours = 0
        else:
            code = data.get('code', DayTypes.EMPTY)
            hours = data.get('hours', 0)
        
        self.calendar_table.update_day_cell(emp_idx, day, code, hours)
    
    # Добавление сотрудника
    def add_employee(self):
        dialog = EmployeeDialog(self)
        if dialog.exec():
            self.employee_added.emit(dialog.result)
            self.status_label.setText("Сотрудник добавлен")
    
    # Редактирование сотрудника
    def edit_employee(self):
        selected_rows = self.employees_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите сотрудника для редактирования")
            return
        
        row = selected_rows[0].row()
        if row < len(self.employees):
            employee = self.employees[row]
            dialog = EmployeeDialog(self, employee)
            if dialog.exec():
                self.employee_edited.emit(row, dialog.result)
                self.status_label.setText("Сотрудник обновлен")
    
    # Удаление сотрудника
    def delete_employee(self):
        selected_rows = self.employees_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите сотрудника для удаления")
            return
        
        row = selected_rows[0].row()
        if row < len(self.employees):
            employee = self.employees[row]
            
            # Создаем диалог
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Подтверждение")
            msg_box.setText(f"Вы действительно хотите удалить сотрудника '{employee.get('name', '')}'?")
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            # Устанавливаем русский текст на кнопках
            msg_box.button(QMessageBox.StandardButton.Yes).setText("Да")
            msg_box.button(QMessageBox.StandardButton.No).setText("Нет")
            
            # Показываем диалог
            reply = msg_box.exec()
            
            if reply == QMessageBox.StandardButton.Yes:
                self.employee_deleted.emit(row)
                self.status_label.setText("Сотрудник удален")
    
    # Обновление таблицы сотрудников
    def update_employees_table(self, employees):
        self.employees = employees
        self.employees_table.setRowCount(len(employees))
        
        for row, employee in enumerate(employees):
            # Сортировка по фамилии уже выполнена в контроллере
            
            # Основные данные
            self.employees_table.setItem(row, 0, QTableWidgetItem(employee.get('name', '')))
            self.employees_table.setItem(row, 1, QTableWidgetItem(employee.get('position', '')))
            self.employees_table.setItem(row, 2, QTableWidgetItem(f"{employee.get('rate', 1.0):.2f}"))
            
            # Статистика за текущий месяц
            month_key = f"{self.current_year}_{self.current_month:02d}"
            month_data = employee.get('months', {}).get(month_key, {})
            
            self.employees_table.setItem(row, 3, QTableWidgetItem(str(month_data.get('working_days', 0))))
            self.employees_table.setItem(row, 4, QTableWidgetItem(str(month_data.get('weekends', 0))))
            self.employees_table.setItem(row, 5, QTableWidgetItem(str(month_data.get('vacation', 0))))
            self.employees_table.setItem(row, 6, QTableWidgetItem(str(month_data.get('sick_leave', 0))))
            self.employees_table.setItem(row, 7, QTableWidgetItem(str(month_data.get('other', 0))))
    
    # Обновление дерева архива
    def update_archive_tree(self, archives):
        self.archive_tree.clear()
        
        for archive in archives:
            item = QTreeWidgetItem([
                archive['month_name'],
                str(archive['year']),
                archive['timestamp'],
                archive['filename']
            ])
            self.archive_tree.addTopLevelItem(item)
    
# ----------------------------------------------------------------------------------------------------------
    
    # Экспорт в Excel
    def export_to_excel(self):
        dialog = ExportDialog(self, self.current_year, self.current_month)
        if dialog.exec():
            self.app.export_to_excel_with_path(
                dialog.selected_path,
                dialog.export_with_stats,
                dialog.export_with_colors
            )
            self.status_label.setText("Табель экспортирован в Excel")