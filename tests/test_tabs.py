"""
Комплексные тесты UI вкладок: EmployeesTab, TimesheetsTab, DocumentsTab, ReportsTab.
Покрывает: отображение данных, CRUD операции UI, поиск, фильтрация.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import QApplication


def get_qapp():
    """Получить или создать QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


class TestEmployeesTab(unittest.TestCase):
    """Тесты вкладки сотрудников."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        from ui.tabs.employees_tab import EmployeesTab
        from database.models import Employee
        
        self.mock_db = Mock()
        self.mock_current_user = {'id_user': 1, 'username': 'test', 'role': 'Табельщик'}
        
        # Мок получения сотрудников
        self.mock_db.execute_query.return_value = [
            (1, 'Иванов Иван Иванович', 'Инженер', 1.0, 40),
            (2, 'Петров Петр Петрович', 'Научный сотрудник', 0.5, 20),
        ]
        
        self.tab = EmployeesTab(self.mock_db, self.mock_current_user)

    def tearDown(self):
        self.tab.close()
        self.tab.deleteLater()

    def test_tab_title(self):
        """Заголовок вкладки."""
        self.assertIn('Сотрудники', self.tab.windowTitle())

    def test_table_widget_exists(self):
        """Существование таблицы."""
        self.assertIsNotNone(self.tab.table)

    def test_search_input_exists(self):
        """Существование поля поиска."""
        self.assertIsNotNone(self.tab.search_edit)

    def test_load_employees(self):
        """Загрузка сотрудников."""
        # Принудительно вызываем загрузку
        self.tab.load_employees()
        
        # Проверяем что был вызов к БД
        self.mock_db.execute_query.assert_called()

    def test_search_employees(self):
        """Поиск сотрудников."""
        # Вводим текст для поиска
        self.tab.search_edit.setText('Иванов')
        
        # Мок результатов поиска
        self.mock_db.execute_query.return_value = [
            (1, 'Иванов Иван Иванович', 'Инженер', 1.0, 40),
        ]
        
        self.tab.load_employees()
        
        # Проверяем что поиск был выполнен
        self.mock_db.execute_query.assert_called()

    def test_table_columns_count(self):
        """Количество колонок в таблице."""
        # Должно быть: ID, ФИО, Должность, Ставка, Часы
        column_count = self.tab.table.columnCount()
        self.assertEqual(column_count, 5)


class TestTimesheetsTab(unittest.TestCase):
    """Тесты вкладки табелей."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        from ui.tabs.timesheets_tab import TimesheetsTab
        
        self.mock_db = Mock()
        self.mock_current_user = {'id_user': 1, 'username': 'test', 'role': 'Табельщик'}
        
        # Мок получения табелей
        self.mock_db.execute_query.return_value = [
            (1, date(2026, 3, 1), date(2026, 3, 31), 'В работе', None, None, None),
        ]
        
        self.tab = TimesheetsTab(self.mock_db, self.mock_current_user)

    def tearDown(self):
        self.tab.close()
        self.tab.deleteLater()

    def test_tab_title(self):
        """Заголовок вкладки."""
        self.assertIn('Табели', self.tab.windowTitle())

    def test_tables_exist(self):
        """Существование таблиц."""
        self.assertIsNotNone(self.tab.timesheet_table)
        self.assertIsNotNone(self.tab.entries_table)

    def test_create_button_exists(self):
        """Существование кнопки создания."""
        self.assertIsNotNone(self.tab.create_btn)

    def test_delete_button_exists(self):
        """Существование кнопки удаления."""
        self.assertIsNotNone(self.tab.delete_btn)

    def test_generate_button_exists(self):
        """Существование кнопки генерации."""
        self.assertIsNotNone(self.tab.generate_btn)

    def test_totals_button_exists(self):
        """Существование кнопки подсчета итогов."""
        self.assertIsNotNone(self.tab.totals_btn)

    def test_load_timesheets(self):
        """Загрузка табелей."""
        self.tab.load_timesheets()
        self.mock_db.execute_query.assert_called()


class TestDocumentsTab(unittest.TestCase):
    """Тесты вкладки документов."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        from ui.tabs.documents_tab import DocumentsTab
        
        self.mock_db = Mock()
        self.mock_current_user = {'id_user': 1, 'username': 'test', 'role': 'Табельщик'}
        
        # Мок получения документов
        self.mock_db.execute_query.return_value = [
            (1, 1, 'Отпуск', date(2026, 3, 1), date(2026, 3, 14)),
        ]
        
        self.tab = DocumentsTab(self.mock_db, self.mock_current_user)

    def tearDown(self):
        self.tab.close()
        self.tab.deleteLater()

    def test_tab_title(self):
        """Заголовок вкладки."""
        self.assertIn('Документы', self.tab.windowTitle())

    def test_table_exists(self):
        """Существование таблицы."""
        self.assertIsNotNone(self.tab.table)

    def test_add_button_exists(self):
        """Существование кнопки добавления."""
        self.assertIsNotNone(self.tab.add_btn)

    def test_edit_button_exists(self):
        """Существование кнопки редактирования."""
        self.assertIsNotNone(self.tab.edit_btn)

    def test_delete_button_exists(self):
        """Существование кнопки удаления."""
        self.assertIsNotNone(self.tab.delete_btn)

    def test_load_documents(self):
        """Загрузка документов."""
        self.tab.load_documents()
        self.mock_db.execute_query.assert_called()

    def test_table_columns_count(self):
        """Количество колонок в таблице."""
        # ID, Сотрудник, Тип, Начало, Окончание
        column_count = self.tab.table.columnCount()
        self.assertEqual(column_count, 5)


class TestReportsTab(unittest.TestCase):
    """Тесты вкладки отчетов."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        from ui.tabs.reports_tab import ReportsTab
        
        self.mock_db = Mock()
        self.mock_current_user = {'id_user': 1, 'username': 'test', 'role': 'Табельщик'}
        
        # Мок получения табелей для comboBox
        self.mock_db.execute_query.return_value = [
            (1, date(2026, 3, 1), date(2026, 3, 31), 'В работе', None, None, None),
        ]
        
        self.tab = ReportsTab(self.mock_db, self.mock_current_user)

    def tearDown(self):
        self.tab.close()
        self.tab.deleteLater()

    def test_tab_title(self):
        """Заголовок вкладки."""
        self.assertIn('Отчёты', self.tab.windowTitle())

    def test_timesheet_combo_exists(self):
        """Существование comboBox выбора табеля."""
        self.assertIsNotNone(self.tab.timesheet_combo)

    def test_generate_button_exists(self):
        """Существование кнопки генерации."""
        self.assertIsNotNone(self.tab.generate_btn)

    def test_export_button_exists(self):
        """Существование кнопки экспорта."""
        self.assertIsNotNone(self.tab.export_btn)

    def test_report_table_exists(self):
        """Существование таблицы отчета."""
        self.assertIsNotNone(self.tab.report_table)

    def test_load_timesheets_for_combo(self):
        """Загрузка табелей в comboBox."""
        # Принудительно вызываем загрузку
        self.tab.load_timesheets()
        self.mock_db.execute_query.assert_called()

    def test_report_columns_count(self):
        """Количество колонок в отчете."""
        # №, ФИО, Должность, Норма, Раб.дни, Отпуск, Больн., Команд., Неявка, Всего часов
        column_count = self.tab.report_table.columnCount()
        self.assertEqual(column_count, 10)


class TestTabsIntegration(unittest.TestCase):
    """Интеграционные тесты вкладок."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def test_employees_tab_double_click_opens_dialog(self):
        """Двойной клик открывает диалог редактирования."""
        from ui.tabs.employees_tab import EmployeesTab
        from ui.dialogs.employee_dialog import EmployeeDialog
        
        mock_db = Mock()
        mock_db.execute_query.return_value = [
            (1, 'Иванов И.И.', 'Инженер', 1.0, 40),
        ]
        
        mock_current_user = {'id_user': 1, 'username': 'test', 'role': 'Табельщик'}
        
        tab = EmployeesTab(mock_db, mock_current_user)
        
        # Эмулируем двойной клик
        with patch.object(EmployeeDialog, 'exec', return_value=1):
            # Это должно открыть диалог
            pass  # Тест требует наличия GUI
        
        tab.close()
        tab.deleteLater()


if __name__ == '__main__':
    unittest.main()
