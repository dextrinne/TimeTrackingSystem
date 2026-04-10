"""
Окно авторизации на PyQt5.
ЛР1-НФ3,НФ4: Разграничение прав доступа, авторизация по логину/паролю.
"""

import hashlib
import os
import json

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from database.db_manager import DatabaseManager


class LoginDialog(QDialog):
    """Окно входа в систему."""

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.current_user = None
        self.remember_file = 'remember.json'
        self.init_ui()
        self.load_remembered_credentials()

    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle('Вход в систему — Учёт рабочего времени')
        self.setFixedSize(420, 380)
        self.setModal(True)

        # Загрузка QSS стиля
        qss_path = os.path.join(os.path.dirname(__file__), '..', 'styles', 'stylesheet.qss')
        with open(qss_path, 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)

        # Заголовок
        title_label = QLabel('Учёт рабочего времени')
        title_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel('ИММИ КубГУ')
        subtitle_label.setStyleSheet('color: gray; font-size: 11px;')
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)

        layout.addSpacing(10)

        # Форма входа
        login_label = QLabel('Логин:')
        layout.addWidget(login_label)
        
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText('Введите логин')
        self.login_edit.setMinimumHeight(35)
        layout.addWidget(self.login_edit)

        password_label = QLabel('Пароль:')
        layout.addWidget(password_label)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText('Введите пароль')
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setMinimumHeight(35)
        self.password_edit.returnPressed.connect(self.login)
        layout.addWidget(self.password_edit)

        # Чекбокс отображения пароля
        self.show_password_checkbox = QCheckBox('Показать пароль')
        layout.addWidget(self.show_password_checkbox)
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)

        layout.addSpacing(5)

        # Чекбокс "Запомнить меня"
        self.remember_checkbox = QCheckBox('Запомнить меня')
        layout.addWidget(self.remember_checkbox)

        layout.addStretch()

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.login_btn = QPushButton('Войти')
        self.login_btn.setMinimumHeight(35)
        self.login_btn.clicked.connect(self.login)

        self.cancel_btn = QPushButton('Отмена')
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        # Фокус на поле логина
        self.login_edit.setFocus()

    def login(self):
        """Обработка входа."""
        username = self.login_edit.text().strip()
        password = self.password_edit.text()

        if not username or not password:
            QMessageBox.warning(self, 'Предупреждение', 'Введите логин и пароль')
            return

        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            row = self.db.execute_query(
                """SELECT id_user, username, password_hash, role, employee_id
                   FROM users WHERE username = %s AND password_hash = %s""",
                (username, password_hash),
                fetchone=True
            )

            if row:
                user_id, db_username, stored_password, role, employee_id = row
                self.current_user = {
                    'id_user': user_id,
                    'username': db_username,
                    'role': role,
                    'employee_id': employee_id
                }
                
                # Сохраняем или очищаем учётные данные
                if self.remember_checkbox.isChecked():
                    self.save_credentials(username, password)
                else:
                    self.clear_credentials()
                
                self.accept()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Неверный логин или пароль')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка входа: {str(e)}')

    def get_user(self):
        """Получить данные текущего пользователя."""
        return self.current_user

    def toggle_password_visibility(self, state):
        """Переключить отображение пароля."""
        if state == Qt.CheckState.Checked.value or state == 2:  # Qt.Checked = 2
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def load_remembered_credentials(self):
        """Загрузить сохранённые учётные данные."""
        if os.path.exists(self.remember_file):
            try:
                with open(self.remember_file, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                self.login_edit.setText(credentials.get('username', ''))
                self.password_edit.setText(credentials.get('password', ''))
                self.remember_checkbox.setChecked(True)
            except (json.JSONDecodeError, KeyError):
                pass

    def save_credentials(self, username, password):
        """Сохранить учётные данные."""
        credentials = {
            'username': username,
            'password': password
        }
        with open(self.remember_file, 'w', encoding='utf-8') as f:
            json.dump(credentials, f, ensure_ascii=False, indent=2)

    def clear_credentials(self):
        """Очистить сохранённые учётные данные."""
        if os.path.exists(self.remember_file):
            os.remove(self.remember_file)
