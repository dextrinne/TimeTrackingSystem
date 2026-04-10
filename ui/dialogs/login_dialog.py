"""
Окно авторизации на PyQt5.
ЛР1-НФ3,НФ4: Разграничение прав доступа, авторизация по логину/паролю.
"""

import hashlib
import os

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
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
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        self.setWindowTitle('Вход в систему — Учёт рабочего времени')
        self.setFixedSize(400, 300)
        self.setModal(True)

        # Загрузка QSS стиля
        qss_path = os.path.join(os.path.dirname(__file__), '..', 'styles', 'stylesheet.qss')
        with open(qss_path, 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Заголовок
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 30, 0, 10)

        title_label = QLabel('Учёт рабочего времени')
        title_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)

        subtitle_label = QLabel('ИММИ КубГУ')
        subtitle_label.setStyleSheet('color: gray; font-size: 11px;')
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle_label)

        layout.addWidget(title_frame)

        # Форма входа
        form_frame = QFrame()
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(10)

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText('Введите логин')
        form_layout.addRow('Логин:', self.login_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText('Введите пароль')
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.returnPressed.connect(self.login)
        form_layout.addRow('Пароль:', self.password_edit)

        layout.addWidget(form_frame)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(40, 0, 40, 10)

        self.login_btn = QPushButton('Войти')
        self.login_btn.clicked.connect(self.login)

        self.cancel_btn = QPushButton('Отмена')
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
                self.accept()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Неверный логин или пароль')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка входа: {str(e)}')

    def get_user(self):
        """Получить данные текущего пользователя."""
        return self.current_user
