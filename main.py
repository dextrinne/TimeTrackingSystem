"""
Точка входа в ПС «Учёт рабочего времени сотрудников института».
ЛР1-ЛР4: Полный функционал системы на PostgreSQL.
UI: PyQt5 с QSS стилями.
"""

import sys
import os
import traceback

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from database.db_manager import DatabaseManager
from ui.dialogs.login_dialog import LoginDialog
from ui.widgets.main_window import MainWindow
from config import DB_CONFIG, APP_CONFIG


def exception_hook(exctype, value, tb):
    """Глобальный обработчик исключений."""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print(f"Необработанное исключение:\n{error_msg}")
    
    # Показываем сообщение об ошибке
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle('Критическая ошибка')
    msg.setText('Произошла критическая ошибка')
    msg.setDetailedText(error_msg)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()
    
    # Сохраняем лог (используем абсолютный путь в директории приложения)
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(app_dir, 'error.log')
        
        # Проверяем размер лога (макс 5MB)
        max_log_size = 5 * 1024 * 1024  # 5 MB
        if os.path.exists(log_file) and os.path.getsize(log_file) > max_log_size:
            # Архивируем старый лог
            old_log = log_file + '.old'
            if os.path.exists(old_log):
                os.remove(old_log)
            os.rename(log_file, old_log)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"\n[{timestamp}] {error_msg}\n")
    except Exception as e:
        print(f"Не удалось сохранить лог: {e}")


sys.excepthook = exception_hook


def main():
    """Главная функция запуска приложения."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_CONFIG['title'])
    app.setApplicationVersion(APP_CONFIG['version'])
    app.setOrganizationName(APP_CONFIG['organization'])

    # Подключение к PostgreSQL
    try:
        db_manager = DatabaseManager(DB_CONFIG)
    except Exception as e:
        QMessageBox.critical(
            None,
            'Ошибка подключения к БД',
            f'Не удалось подключиться к PostgreSQL:\n\n{str(e)}\n\n'
            f'Проверьте:\n'
            f'  1. Запущен ли PostgreSQL\n'
            f'  2. Настройки в config.py:\n'
            f'     Хост: {DB_CONFIG["host"]}\n'
            f'     Порт: {DB_CONFIG["port"]}\n'
            f'     База: {DB_CONFIG["database"]}\n'
            f'     Пользователь: {DB_CONFIG["user"]}\n'
            f'     Пароль: {DB_CONFIG["password"]}\n\n'
            f'Для создания БД выполните:\n'
            f'  python database/init_db.py'
        )
        sys.exit(1)

    # Проверка работоспособности БД
    try:
        db_manager.execute_query("SELECT 1", fetchone=True)
    except Exception as e:
        QMessageBox.critical(
            None,
            'Ошибка',
            f'База данных недоступна:\n{str(e)}\n\n'
            f'Для инициализации выполните:\n'
            f'  python database/init_db.py'
        )
        db_manager.close_all()
        sys.exit(1)

    # Запускаем окно авторизации
    login_dialog = LoginDialog(db_manager)
    if login_dialog.exec() != 1:
        db_manager.close_all()
        sys.exit(0)

    current_user = login_dialog.get_user()

    if current_user:
        main_window = MainWindow(db_manager, current_user)
        main_window.show()
        sys.exit(app.exec())
    else:
        db_manager.close_all()
        sys.exit(0)


if __name__ == '__main__':
    main()
