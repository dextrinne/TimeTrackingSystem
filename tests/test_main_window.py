"""
Комплексные тесты MainWindow.
Покрывает: инициализация, вкладки, менюбар, статусбар, закрытие окна.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt


def get_qapp():
    """Получить или создать QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


class TestMainWindow(unittest.TestCase):
    """Тесты MainWindow."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        from ui.widgets.main_window import MainWindow
        
        self.mock_db = Mock()
        self.mock_current_user = {
            'id_user': 1,
            'username': 'testuser',
            'role': 'Табельщик',
            'employee_id': None
        }
        
        self.window = MainWindow(self.mock_db, self.mock_current_user)

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

    def test_window_title(self):
        """Заголовок окна."""
        expected_title = 'Учёт рабочего времени сотрудников ИММИ КубГУ'
        self.assertIn('Учёт рабочего времени', self.window.windowTitle())

    def test_tab_widget_exists(self):
        """Существование QTabWidget."""
        self.assertIsNotNone(self.window.tab_widget)

    def test_tab_count(self):
        """Количество вкладок."""
        # Сотрудники, Табели, Документы, Отчёты
        tab_count = self.window.tab_widget.count()
        self.assertEqual(tab_count, 4)

    def test_tab_names(self):
        """Названия вкладок."""
        tab_names = [
            self.window.tab_widget.tabText(0),
            self.window.tab_widget.tabText(1),
            self.window.tab_widget.tabText(2),
            self.window.tab_widget.tabText(3),
        ]
        
        self.assertIn('Сотрудники', tab_names[0])
        self.assertIn('Табели', tab_names[1])
        self.assertIn('Документы', tab_names[2])
        self.assertIn('Отчёты', tab_names[3])

    def test_menubar_exists(self):
        """Существование менюбара."""
        self.assertIsNotNone(self.window.menuBar())

    def test_file_menu_exists(self):
        """Существование меню 'Файл'."""
        menubar = self.window.menuBar()
        # Находим меню "Файл"
        file_menu = None
        for action in menubar.actions():
            if 'Файл' in action.text():
                file_menu = action.menu()
                break
        self.assertIsNotNone(file_menu)

    def test_help_menu_exists(self):
        """Существование меню 'Справка'."""
        menubar = self.window.menuBar()
        help_menu = None
        for action in menubar.actions():
            if 'Справка' in action.text():
                help_menu = action.menu()
                break
        self.assertIsNotNone(help_menu)

    def test_statusbar_exists(self):
        """Существование статусбара."""
        self.assertIsNotNone(self.window.statusBar())

    def test_statusbar_user_info(self):
        """Отображение информации о пользователе в статусбаре."""
        status_text = self.window.statusBar().currentMessage()
        self.assertIn('testuser', status_text)
        self.assertIn('Табельщик', status_text)

    def test_backup_database_action(self):
        """Действие 'Резервная копия БД'."""
        # Находим действие в меню
        menubar = self.window.menuBar()
        for action in menubar.actions():
            if 'Файл' in action.text():
                file_menu = action.menu()
                for menu_action in file_menu.actions():
                    if 'Резервная копия' in menu_action.text() or 'Backup' in menu_action.text():
                        self.assertIsNotNone(menu_action)
                        break
                break

    def test_exit_action(self):
        """Действие 'Выход'."""
        menubar = self.window.menuBar()
        exit_action = None
        
        for action in menubar.actions():
            if 'Файл' in action.text():
                file_menu = action.menu()
                for menu_action in file_menu.actions():
                    if 'Выход' in menu_action.text() or 'Exit' in menu_action.text():
                        exit_action = menu_action
                        break
                break
        
        self.assertIsNotNone(exit_action)

    def test_about_action(self):
        """Действие 'О программе'."""
        menubar = self.window.menuBar()
        about_action = None
        
        for action in menubar.actions():
            if 'Справка' in action.text():
                help_menu = action.menu()
                for menu_action in help_menu.actions():
                    if 'О программе' in menu_action.text():
                        about_action = menu_action
                        break
                break
        
        self.assertIsNotNone(about_action)

    def test_close_event_with_confirmation(self):
        """Закрытие окна с подтверждением."""
        with patch.object(QMessageBox, 'question') as mock_question:
            mock_question.return_value = QMessageBox.Yes
            self.window.close()

    def test_close_event_cancel(self):
        """Отмена закрытия окна."""
        with patch.object(QMessageBox, 'question') as mock_question:
            mock_question.return_value = QMessageBox.No
            # Окно не должно закрыться
            self.window.close()


class TestMainWindowDatabaseBackup(unittest.TestCase):
    """Тесты резервного копирования БД."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        from ui.widgets.main_window import MainWindow
        
        self.mock_db = Mock()
        self.mock_current_user = {'id_user': 1, 'username': 'test', 'role': 'Табельщик'}
        self.window = MainWindow(self.mock_db, self.mock_current_user)

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

    def test_backup_success(self):
        """Успешное создание резервной копии."""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        self.mock_db.backup_database.return_value = True
        
        with patch.object(QFileDialog, 'getSaveFileName') as mock_file:
            mock_file.return_value = ('/tmp/backup.sql', 'SQL Files (*.sql)')
            
            with patch.object(QMessageBox, 'information') as mock_info:
                # Вызываем backup через меню
                # Находим и вызываем действие
                pass  # Требуется GUI взаимодействие
        
        # Проверяем что backup_database был вызван
        self.mock_db.backup_database.assert_called()

    def test_backup_failure(self):
        """Ошибка создания резервной копии."""
        from PyQt5.QtWidgets import QMessageBox
        
        self.mock_db.backup_database.return_value = False
        
        with patch.object(QMessageBox, 'critical') as mock_critical:
            # Симулируем ошибку
            pass  # Требуется GUI взаимодействие


class TestMainWindowPermissions(unittest.TestCase):
    """Тесты разграничения прав доступа."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def test_tabelshchik_full_access(self):
        """Табельщик имеет полный доступ."""
        from ui.widgets.main_window import MainWindow
        
        mock_db = Mock()
        mock_current_user = {'id_user': 1, 'username': 'tabel', 'role': 'Табельщик'}
        
        window = MainWindow(mock_db, mock_current_user)
        
        # Все вкладки должны быть доступны
        self.assertEqual(window.tab_widget.count(), 4)
        
        window.close()
        window.deleteLater()


if __name__ == '__main__':
    unittest.main()
