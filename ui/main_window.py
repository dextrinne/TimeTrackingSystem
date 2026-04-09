"""
Главное окно приложения на tkinter.
ЛР1-НФ2: Интуитивный GUI с меню и панелями инструментов.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from ui.employee_tab import EmployeeTab
from ui.timesheet_tab import TimesheetTab
from ui.document_tab import DocumentTab
from ui.report_tab import ReportTab


class MainWindow(tk.Tk):
    """Главное окно приложения."""

    def __init__(self, db_manager, current_user):
        super().__init__()
        self.db = db_manager
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        self.title('Учёт рабочего времени сотрудников ИММИ КубГУ')
        self.geometry('1200x800')
        self.minsize(900, 600)

        # Создаём меню
        self.create_menu()

        # Создаём панель инструментов
        self.create_toolbar()

        # Notebook с вкладками
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Вкладки
        self.employee_tab = EmployeeTab(self.notebook, self.db, self.current_user)
        self.notebook.add(self.employee_tab, text='  Сотрудники  ')

        self.timesheet_tab = TimesheetTab(self.notebook, self.db, self.current_user)
        self.notebook.add(self.timesheet_tab, text='  Табели  ')

        self.document_tab = DocumentTab(self.notebook, self.db, self.current_user)
        self.notebook.add(self.document_tab, text='  Документы  ')

        self.report_tab = ReportTab(self.notebook, self.db, self.current_user)
        self.notebook.add(self.report_tab, text='  Отчёты  ')

        # Строка состояния
        self.status_bar = ttk.Frame(self)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            self.status_bar,
            text=f"Пользователь: {self.current_user['username']} ({self.current_user['role']}) | {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=2)

        # Обработка закрытия
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_menu(self):
        """Создание меню приложения."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Файл', menu=file_menu)
        file_menu.add_command(label='Создать резервную копию БД', command=self.backup_database)
        file_menu.add_separator()
        file_menu.add_command(label='Выход', accelerator='Ctrl+Q', command=self.on_close)
        self.bind('<Control-q>', lambda e: self.on_close())

        # Меню "Справочники"
        ref_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Справочники', menu=ref_menu)
        ref_menu.add_command(label='Сотрудники', command=lambda: self.notebook.select(0))

        # Меню "Табель"
        ts_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Табель', menu=ts_menu)
        ts_menu.add_command(label='Управление табелями', command=lambda: self.notebook.select(1))

        # Меню "Документы"
        doc_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Документы', menu=doc_menu)
        doc_menu.add_command(label='Управление документами', command=lambda: self.notebook.select(2))

        # Меню "Отчёты"
        report_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Отчёты', menu=report_menu)
        report_menu.add_command(label='Формирование отчётов', command=lambda: self.notebook.select(3))

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Справка', menu=help_menu)
        help_menu.add_command(label='О программе', command=self.show_about)

    def create_toolbar(self):
        """Создание панели инструментов."""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(toolbar, text='👥 Сотрудники', command=lambda: self.notebook.select(0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text='📋 Табели', command=lambda: self.notebook.select(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text='📄 Документы', command=lambda: self.notebook.select(2)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text='📊 Отчёты', command=lambda: self.notebook.select(3)).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Button(toolbar, text='💾 Backup БД', command=self.backup_database).pack(side=tk.LEFT, padx=2)

    def backup_database(self):
        """Создание резервной копии БД."""
        file_path = filedialog.asksaveasfilename(
            title='Сохранить резервную копию',
            defaultextension='.sql',
            filetypes=[('SQL Files', '*.sql')],
            initialfilename=f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
        )
        
        if file_path:
            try:
                success = self.db.backup_database(file_path)
                if success:
                    messagebox.showinfo('Успех', 'Резервная копия создана успешно')
                else:
                    messagebox.showwarning('Ошибка', 'Не удалось создать резервную копию')
            except Exception as e:
                messagebox.showerror('Ошибка', f'Ошибка: {str(e)}')

    def show_about(self):
        """Показать окно "О программе"."""
        about_window = tk.Toplevel(self)
        about_window.title('О программе')
        about_window.geometry('400x250')
        about_window.resizable(False, False)
        about_window.transient(self)
        about_window.grab_set()

        ttk.Label(about_window, text='Учёт рабочего времени сотрудников', font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Label(about_window, text='Версия: 1.0.0').pack()
        ttk.Label(about_window, text='ИММИ КубГУ, 2026').pack()
        ttk.Label(about_window, text='Лабораторные работы №1-4').pack()
        ttk.Label(about_window, text='Выполнила: Чупрова С.Н., гр. МО-32-2').pack()
        
        ttk.Button(about_window, text='Закрыть', command=about_window.destroy).pack(pady=20)

    def on_close(self):
        """Обработка закрытия окна."""
        if messagebox.askyesno('Выход', 'Вы уверены, что хотите выйти?'):
            self.db.close_all()
            self.destroy()
