"""
Главное окно приложения на PyQt5.
ЛР1-НФ2: Интуитивный GUI с меню и панелями инструментов.
"""

import os
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QMenuBar,
    QMessageBox, QFileDialog, QLabel, QAction
)
from PyQt5.QtGui import QKeySequence

from ui.tabs.employees_tab import EmployeesTab
from ui.tabs.timesheets_tab import TimesheetsTab
from ui.tabs.documents_tab import DocumentsTab
from ui.tabs.reports_tab import ReportsTab


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self, db_manager, current_user, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle('Учёт рабочего времени сотрудников ИММИ КубГУ')
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)

        # Загрузка QSS стиля
        qss_path = os.path.join(os.path.dirname(__file__), '..', 'styles', 'stylesheet.qss')
        with open(qss_path, 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

        # Создаём меню
        self.create_menu()

        # QTabWidget с вкладками
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Вкладки
        self.employees_tab = EmployeesTab(self.db, self.current_user)
        self.tab_widget.addTab(self.employees_tab, 'Сотрудники')

        self.timesheets_tab = TimesheetsTab(self.db, self.current_user)
        self.tab_widget.addTab(self.timesheets_tab, 'Табели')

        self.documents_tab = DocumentsTab(self.db, self.current_user)
        self.tab_widget.addTab(self.documents_tab, 'Документы')

        self.reports_tab = ReportsTab(self.db, self.current_user)
        self.tab_widget.addTab(self.reports_tab, 'Отчёты')

        # Строка состояния
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        user_label = QLabel(
            f"Пользователь: {self.current_user['username']} ({self.current_user['role']}) | {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        self.status_bar.addPermanentWidget(user_label)

    def create_menu(self):
        """Создание меню приложения."""
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')

        backup_action = QAction('Создать резервную копию БД', self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)

        file_menu.addSeparator()

        exit_action = QAction('Выход', self)
        exit_action.setShortcut(QKeySequence('Ctrl+Q'))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Справка"
        help_menu = menubar.addMenu('Справка')

        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def backup_database(self):
        """Создание резервной копии БД."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Сохранить резервную копию',
            f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql',
            'SQL Files (*.sql)'
        )

        if file_path:
            try:
                success = self.db.backup_database(file_path)
                if success:
                    QMessageBox.information(self, 'Успех', 'Резервная копия создана успешно')
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось создать резервную копию')
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Ошибка: {str(e)}')

    def show_about(self):
        """Показать окно "О программе"."""
        QMessageBox.about(
            self,
            'О программе',
            '<h2>Учёт рабочего времени сотрудников</h2>'
            '<p>Версия: 1.0.0</p>'
            '<p>ИММИ КубГУ, 2026</p>'
            '<p>Лабораторные работы №1-4</p>'
            '<p>Выполнила: Чупрова С.Н., гр. МО-32-2</p>'
        )

    def closeEvent(self, event):
        """Обработка закрытия окна."""
        reply = QMessageBox.question(
            self, 'Выход',
            'Вы уверены, что хотите выйти?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.close_all()
            event.accept()
        else:
            event.ignore()
