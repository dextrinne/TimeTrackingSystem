import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from core.time_table_app import TimeTableApp
from frontend.config import AppConfig


def main():
    """Запуск главного приложения"""
    # Создаем необходимые директории
    AppConfig.ensure_directories()
    
    # Запускаем приложение
    root = tk.Tk()
    app = TimeTableApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: app.on_closing())
    root.mainloop()


if __name__ == "__main__":
    main()