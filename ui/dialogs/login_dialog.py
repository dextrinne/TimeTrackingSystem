"""
Окно авторизации на PyQt5.
ЛР1-НФ3,НФ4: Разграничение прав доступа, авторизация по логину/паролю.
"""

import hashlib
import os
import json
import base64

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from database.db_manager import DatabaseManager

# Импортируем cryptography для шифрования
try:
    from cryptography.fernet import Fernet
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    print("Предупреждение: cryptography не установлен. Пароли будут сохраняться в открытом виде.")
    print("Установите: pip install cryptography")

# Импортируем bcrypt для хеширования паролей
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False
    print("Предупреждение: bcrypt не установлен. Используется SHA-256 (менее безопасно).")
    print("Установите: pip install bcrypt")


class LoginDialog(QDialog):
    """Окно входа в систему."""

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.current_user = None
        # Используем абсолютный путь в директории приложения
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.remember_file = os.path.join(app_dir, 'remember.json')
        self.key_file = os.path.join(app_dir, 'remember.key')
        self.init_ui()
        self.load_remembered_credentials()

    def _get_encryption_key(self):
        """Получить или создать ключ шифрования."""
        if not HAS_CRYPTOGRAPHY:
            return None
        
        try:
            # Пробуем прочитать существующий ключ
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    return f.read()
            else:
                # Создаём новый ключ
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                # Устанавливаем права доступа только для чтения владельцу
                try:
                    os.chmod(self.key_file, 0o600)
                except:
                    pass
                return key
        except Exception as e:
            print(f"Ошибка работы с ключом шифрования: {e}")
            return None

    def _encrypt_password(self, password):
        """Зашифровать пароль."""
        key = self._get_encryption_key()
        if not key:
            return password  # Без шифрования возвращаем как есть
        
        fernet = Fernet(key)
        encrypted = fernet.encrypt(password.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def _decrypt_password(self, encrypted_password):
        """Расшифровать пароль."""
        key = self._get_encryption_key()
        if not key:
            return encrypted_password  # Без шифрования возвращаем как есть
        
        try:
            fernet = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
            return fernet.decrypt(encrypted_bytes).decode()
        except Exception as e:
            print(f"Ошибка расшифровки пароля: {e}")
            return None

    def _hash_password(self, password):
        """Хешировать пароль с использованием bcrypt или SHA-256."""
        if HAS_BCRYPT:
            # bcrypt автоматически генерирует соль
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        else:
            # Fallback на SHA-256 (менее безопасно)
            return hashlib.sha256(password.encode()).hexdigest()

    def _check_password(self, password, stored_hash):
        """Проверить пароль против хеша."""
        if HAS_BCRYPT:
            # bcrypt.checkpw ожидает bytes
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        else:
            # SHA-256 сравнение
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            return password_hash == stored_hash

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
            # Сначала получаем хеш из БД
            row = self.db.execute_query(
                """SELECT id_user, username, password_hash, role, employee_id
                   FROM users WHERE username = %s""",
                (username,),
                fetchone=True
            )

            if row:
                user_id, db_username, stored_password_hash, role, employee_id = row
                
                # Проверяем пароль с использованием bcrypt или SHA-256
                if self._check_password(password, stored_password_hash):
                    self.current_user = {
                        'id_user': user_id,
                        'username': db_username,
                        'role': role,
                        'employee_id': employee_id
                    }

                    # Сохраняем или очищаем учётные данные
                    try:
                        if self.remember_checkbox.isChecked():
                            self.save_credentials(username, password)
                        else:
                            self.clear_credentials()
                    except Exception as e:
                        # Не блокируем вход из-за ошибок сохранения
                        print(f"Ошибка при сохранении/очистке: {e}")

                    self.accept()
                else:
                    QMessageBox.critical(self, 'Ошибка', 'Неверный логин или пароль')
            else:
                QMessageBox.critical(self, 'Ошибка', 'Неверный логин или пароль')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка входа: {str(e)}')

    def get_user(self):
        """Получить данные текущего пользователя."""
        return self.current_user

    def toggle_password_visibility(self, state):
        """Переключить отображение пароля."""
        # Qt.Checked = 2, Qt.Unchecked = 0
        if state == 2:  # Checked
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def load_remembered_credentials(self):
        """Загрузить сохранённые учётные данные (с расшифровкой пароля)."""
        try:
            if os.path.exists(self.remember_file):
                with open(self.remember_file, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                
                username = credentials.get('username', '')
                encrypted_password = credentials.get('password', '')
                is_encrypted = credentials.get('encrypted', False)
                
                # Расшифровываем пароль если он зашифрован
                if is_encrypted and HAS_CRYPTOGRAPHY:
                    password = self._decrypt_password(encrypted_password)
                    if password is None:
                        # Ошибка расшифровки - очищаем данные
                        print("Не удалось расшифровать пароль. Файл будет удалён.")
                        self.clear_credentials()
                        return
                else:
                    # Старый формат (не зашифрован) или нет cryptography
                    password = encrypted_password
                
                self.login_edit.setText(username)
                self.password_edit.setText(password)
                self.remember_checkbox.setChecked(True)
        except (json.JSONDecodeError, KeyError, IOError, OSError) as e:
            # Если файл повреждён или недоступен - просто игнорируем
            print(f"Предупреждение: не удалось загрузить сохранённые данные: {e}")
        except Exception as e:
            # Любые другие ошибки при загрузке
            print(f"Ошибка при загрузке сохранённых данных: {e}")

    def save_credentials(self, username, password):
        """Сохранить учётные данные (пароль шифруется)."""
        try:
            # Шифруем пароль
            encrypted_password = self._encrypt_password(password)
            
            credentials = {
                'username': username,
                'password': encrypted_password,
                'encrypted': HAS_CRYPTOGRAPHY  # Флаг что пароль зашифрован
            }
            with open(self.remember_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, ensure_ascii=False, indent=2)
        except (IOError, OSError, PermissionError) as e:
            print(f"Ошибка сохранения учётных данных: {e}")
            QMessageBox.warning(
                self,
                'Предупреждение',
                f'Не удалось сохранить учётные данные:\n{e}'
            )
        except Exception as e:
            print(f"Неизвестная ошибка при сохранении: {e}")

    def clear_credentials(self):
        """Очистить сохранённые учётные данные."""
        try:
            if os.path.exists(self.remember_file):
                os.remove(self.remember_file)
        except (IOError, OSError, PermissionError) as e:
            print(f"Ошибка удаления учётных данных: {e}")
        except Exception as e:
            print(f"Неизвестная ошибка при удалении: {e}")
