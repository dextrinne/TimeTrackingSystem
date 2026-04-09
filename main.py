"""
Точка входа в ПС «Учёт рабочего времени сотрудников института».
ЛР1-ЛР4: Полный функционал системы на PostgreSQL.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

from database.db_manager import DatabaseManager
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from config import DB_CONFIG, APP_CONFIG


def main():
    """Главная функция запуска приложения."""
    # Подключение к PostgreSQL
    try:
        db_manager = DatabaseManager(DB_CONFIG)
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
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
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            'Ошибка',
            f'База данных недоступна:\n{str(e)}\n\n'
            f'Для инициализации выполните:\n'
            f'  python database/init_db.py'
        )
        sys.exit(1)

    # Запускаем окно авторизации
    login_window = LoginWindow(db_manager)
    login_window.wait_window()
    
    current_user = login_window.get_user()
    
    if current_user:
        # Запускаем главное окно
        main_window = MainWindow(db_manager, current_user)
        main_window.mainloop()
    else:
        db_manager.close_all()
        sys.exit(0)


if __name__ == '__main__':
    main()
