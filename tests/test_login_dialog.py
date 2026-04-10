"""
Комплексные тесты UI компонентов: LoginDialog.
Покрывает: инициализация, ввод данных, валидация, переключение видимости пароля, запоминание.
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import QApplication, QCheckBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

# Создаем QApplication один раз для всех тестов
def get_qapp():
    """Получить или создать QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


class TestLoginDialogUI(unittest.TestCase):
    """Тесты UI LoginDialog."""

    @classmethod
    def setUpClass(cls):
        """Создание QApplication для всех тестов."""
        cls.app = get_qapp()

    def setUp(self):
        """Настройка: создание мока БД и диалога."""
        from ui.dialogs.login_dialog import LoginDialog
        
        self.mock_db = Mock()
        self.dialog = LoginDialog(self.mock_db)
        
    def tearDown(self):
        """Очистка после каждого теста."""
        self.dialog.close()
        self.dialog.deleteLater()
        
        # Удаляем файл remember.json если существует
        remember_file = 'remember.json'
        if os.path.exists(remember_file):
            os.remove(remember_file)

    def test_dialog_initial_state(self):
        """Проверка начального состояния диалога."""
        self.assertEqual(self.dialog.windowTitle(), 'Вход в систему — Учёт рабочего время')
        self.assertEqual(self.dialog.login_edit.text(), '')
        self.assertEqual(self.dialog.password_edit.text(), '')
        self.assertFalse(self.dialog.remember_checkbox.isChecked())
        self.assertFalse(self.dialog.show_password_checkbox.isChecked())

    def test_password_hidden_by_default(self):
        """Пароль скрыт по умолчанию."""
        self.assertEqual(
            self.dialog.password_edit.echoMode(),
            QLineEdit.EchoMode.Password
        )

    def test_toggle_password_visibility(self):
        """Переключение видимости пароля."""
        # Включаем отображение
        self.dialog.show_password_checkbox.setChecked(True)
        self.assertEqual(
            self.dialog.password_edit.echoMode(),
            QLineEdit.EchoMode.Normal
        )
        
        # Выключаем отображение
        self.dialog.show_password_checkbox.setChecked(False)
        self.assertEqual(
            self.dialog.password_edit.echoMode(),
            QLineEdit.EchoMode.Password
        )

    def test_login_button_exists(self):
        """Проверка существования кнопки 'Войти'."""
        self.assertIsNotNone(self.dialog.login_btn)
        self.assertEqual(self.dialog.login_btn.text(), 'Войти')

    def test_cancel_button_exists(self):
        """Проверка существования кнопки 'Отмена'."""
        self.assertIsNotNone(self.dialog.cancel_btn)
        self.assertEqual(self.dialog.cancel_btn.text(), 'Отмена')

    def test_login_fields_placeholders(self):
        """Проверка placeholder текста."""
        self.assertEqual(self.dialog.login_edit.placeholderText(), 'Введите логин')
        self.assertEqual(self.dialog.password_edit.placeholderText(), 'Введите пароль')

    def test_remember_checkbox_text(self):
        """Проверка текста чекбокса 'Запомнить меня'."""
        self.assertEqual(self.dialog.remember_checkbox.text(), 'Запомнить меня')

    def test_show_password_checkbox_text(self):
        """Проверка текста чекбокса 'Показать пароль'."""
        self.assertEqual(self.dialog.show_password_checkbox.text(), 'Показать пароль')

    def test_login_with_empty_credentials(self):
        """Попытка входа с пустыми данными."""
        from PyQt5.QtWidgets import QMessageBox
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.dialog.login()
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            self.assertIn('логин', args[1].lower())

    def test_login_with_only_username(self):
        """Попытка входа только с логином."""
        from PyQt5.QtWidgets import QMessageBox
        
        self.dialog.login_edit.setText('testuser')
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.dialog.login()
            mock_warning.assert_called_once()

    def test_login_with_only_password(self):
        """Попытка входа только с паролем."""
        from PyQt5.QtWidgets import QMessageBox
        
        self.dialog.password_edit.setText('password')
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.dialog.login()
            mock_warning.assert_called_once()

    def test_successful_login(self):
        """Успешный вход."""
        import hashlib
        password = 'testpass123'
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        self.dialog.login_edit.setText('testuser')
        self.dialog.password_edit.setText(password)
        
        # Мок ответа БД
        self.mock_db.execute_query.return_value = (
            1, 'testuser', password_hash, 'Табельщик', None
        )
        
        result = self.dialog.exec()
        
        # Проверяем что запрос к БД был выполнен
        self.mock_db.execute_query.assert_called_once()
        
        # Проверяем что пользователь установлен
        self.assertIsNotNone(self.dialog.current_user)
        self.assertEqual(self.dialog.current_user['username'], 'testuser')

    def test_failed_login_wrong_credentials(self):
        """Неуспешный вход - неверные данные."""
        from PyQt5.QtWidgets import QMessageBox
        
        self.dialog.login_edit.setText('wronguser')
        self.dialog.password_edit.setText('wrongpass')
        
        # Мок пустого ответа БД
        self.mock_db.execute_query.return_value = None
        
        with patch.object(QMessageBox, 'critical') as mock_critical:
            self.dialog.login()
            mock_critical.assert_called_once()
            args = mock_critical.call_args[0]
            self.assertIn('неверн', args[1].lower())

    def test_save_credentials_on_login(self):
        """Сохранение учётных данных при входе."""
        import hashlib
        password = 'testpass123'
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        self.dialog.login_edit.setText('testuser')
        self.dialog.password_edit.setText(password)
        self.dialog.remember_checkbox.setChecked(True)
        
        self.mock_db.execute_query.return_value = (
            1, 'testuser', password_hash, 'Табельщик', None
        )
        
        self.dialog.login()
        
        # Проверяем что файл создан
        remember_file = 'remember.json'
        self.assertTrue(os.path.exists(remember_file))
        
        with open(remember_file, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
            self.assertEqual(credentials['username'], 'testuser')
            self.assertEqual(credentials['password'], password)

    def test_clear_credentials_on_uncheck(self):
        """Очистка учётных данных при снятии галочки."""
        import hashlib
        password = 'testpass123'
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Сначала сохраняем
        remember_file = 'remember.json'
        with open(remember_file, 'w', encoding='utf-8') as f:
            json.dump({'username': 'olduser', 'password': 'oldpass'}, f)
        
        self.dialog.login_edit.setText('testuser')
        self.dialog.password_edit.setText(password)
        self.dialog.remember_checkbox.setChecked(False)  # Не запоминаем
        
        self.mock_db.execute_query.return_value = (
            1, 'testuser', password_hash, 'Табельщик', None
        )
        
        self.dialog.login()
        
        # Файл должен быть удален
        self.assertFalse(os.path.exists(remember_file))

    def test_load_remembered_credentials(self):
        """Загрузка сохранённых учётных данных."""
        remember_file = 'remember.json'
        credentials = {'username': 'remembered_user', 'password': 'remembered_pass'}
        
        with open(remember_file, 'w', encoding='utf-8') as f:
            json.dump(credentials, f)
        
        # Создаем новый диалог - он должен загрузить данные
        from ui.dialogs.login_dialog import LoginDialog
        dialog2 = LoginDialog(self.mock_db)
        
        self.assertEqual(dialog2.login_edit.text(), 'remembered_user')
        self.assertEqual(dialog2.password_edit.text(), 'remembered_pass')
        self.assertTrue(dialog2.remember_checkbox.isChecked())
        
        dialog2.close()
        dialog2.deleteLater()
        
        # Чистим
        if os.path.exists(remember_file):
            os.remove(remember_file)

    def test_password_visibility_toggle_via_checkbox(self):
        """Переключение видимости пароля через чекбокс."""
        # Вводим пароль
        self.dialog.password_edit.setText('secret')
        
        # По умолчанию скрыт
        self.assertEqual(self.dialog.password_edit.text(), 'secret')
        self.assertEqual(self.dialog.password_edit.echoMode(), QLineEdit.EchoMode.Password)
        
        # Показываем
        self.dialog.show_password_checkbox.setChecked(True)
        self.assertEqual(self.dialog.password_edit.echoMode(), QLineEdit.EchoMode.Normal)
        
        # Скрываем снова
        self.dialog.show_password_checkbox.setChecked(False)
        self.assertEqual(self.dialog.password_edit.echoMode(), QLineEdit.EchoMode.Password)


class TestLoginDialogDatabaseError(unittest.TestCase):
    """Тесты обработки ошибок БД в LoginDialog."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        from ui.dialogs.login_dialog import LoginDialog
        self.mock_db = Mock()
        self.dialog = LoginDialog(self.mock_db)

    def tearDown(self):
        self.dialog.close()
        self.dialog.deleteLater()

    def test_login_database_error(self):
        """Ошибка при подключении к БД."""
        from PyQt5.QtWidgets import QMessageBox
        
        self.dialog.login_edit.setText('user')
        self.dialog.password_edit.setText('pass')
        
        self.mock_db.execute_query.side_effect = Exception("DB Connection Error")
        
        with patch.object(QMessageBox, 'critical') as mock_critical:
            self.dialog.login()
            mock_critical.assert_called_once()
            args = mock_critical.call_args[0]
            self.assertIn('ошибк', args[1].lower())


if __name__ == '__main__':
    unittest.main()
