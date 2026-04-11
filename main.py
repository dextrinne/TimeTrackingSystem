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
    
    # Сохраняем лог
    try:
        with open('error.log', 'a', encoding='utf-8') as f:
            f.write(f"\n{error_msg}\n")
    except:
        pass


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
