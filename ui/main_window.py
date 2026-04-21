import tkinter as tk
from tkinter import ttk
import os
import json
from datetime import datetime
import calendar

from frontend.styles import DayTypes, Colors, Fonts
from frontend.config import AppConfig
from ui.widgets import CalendarGrid


class MainWindow:
    """Главное окно с вкладками"""
    
    def __init__(self, root, app):
        self.root = root
        self.app = app
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса с вкладками"""
        # Верхняя панель
        top_frame = ttk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="📊 Экспортировать в Excel", 
                command=self.app.export_to_excel).pack(side=tk.LEFT, padx=5)
        ttk.Label(top_frame, text="💾 Автосохранение включено", 
                foreground=Colors.SUCCESS, font=Fonts.SMALL).pack(side=tk.LEFT, padx=20)
        
        # Информация о типах дней
        info_frame = ttk.Frame(self.root)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        ttk.Label(info_frame, text="Основные типы: ", font=Fonts.BOLD).pack(side=tk.LEFT)
        
        # Показываем только основные типы
        main_types_info = [
            (DayTypes.WORKDAY, 'Рабочий'),
            (DayTypes.WEEKEND, 'Выходной'),
            (DayTypes.VACATION_MAIN, 'Отпуск'),
            (DayTypes.SICK, 'Больничный'),
            (DayTypes.BUSINESS_TRIP, 'Командировка'),
        ]
        
        for code, name in main_types_info:
            _, color, short = DayTypes.TYPES[code]
            
            frame = tk.Frame(info_frame, bg=color, relief=tk.RAISED, bd=1)
            frame.pack(side=tk.LEFT, padx=2)
            
            label = tk.Label(frame, text=f"{short} - {name}", bg=color, fg=Colors.TEXT,
                            padx=6, pady=2, font=Fonts.SMALL)
            label.pack()
        
        ttk.Label(info_frame, text="    Левый клик: основные типы  |  Правый клик: все типы", 
                foreground=Colors.INFO, font=Fonts.SMALL).pack(side=tk.LEFT, padx=20)
        
        # Создание Notebook с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка Табель
        self.timetable_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.timetable_frame, text="📅 Табель")
        self.setup_timetable_tab()
        
        # Вкладка Сотрудники
        self.employees_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.employees_frame, text="👥 Сотрудники")
        self.setup_employees_tab()
        
        # Вкладка Архив табелей
        self.archive_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.archive_frame, text="📦 Архив")
        self.setup_archive_tab()
    
    def setup_timetable_tab(self):
        """Настройка вкладки с табелем"""
        # Контроль месяца
        control_frame = ttk.Frame(self.timetable_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Месяц:").pack(side=tk.LEFT, padx=(0, 5))
        self.month_var = tk.StringVar(value=AppConfig.MONTHS[AppConfig.DEFAULT_MONTH - 1])
        month_combo = ttk.Combobox(control_frame, textvariable=self.month_var, 
                                   values=AppConfig.MONTHS, width=12, state='readonly')
        month_combo.pack(side=tk.LEFT, padx=5)
        month_combo.bind('<<ComboboxSelected>>', 
                        lambda e: self.app.on_month_changed(self.month_var.get()))
        
        ttk.Label(control_frame, text="Год:").pack(side=tk.LEFT, padx=(20, 5))
        self.year_var = tk.StringVar(value=str(AppConfig.DEFAULT_YEAR))
        year_spin = ttk.Spinbox(control_frame, from_=2020, to=2030, textvariable=self.year_var, 
                               command=lambda: self.app.on_year_changed(self.year_var.get()), width=5)
        year_spin.pack(side=tk.LEFT, padx=5)
        
        # Canvas с прокруткой
        main_frame = ttk.Frame(self.timetable_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(main_frame, bg=Colors.WHITE, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=Colors.WHITE)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Создание табеля
        self.create_timetable()
    
    def create_timetable(self):
        """Создание табеля с использованием CalendarGrid"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.app.day_buttons = {}
        self.app.days_in_month = calendar.monthrange(
            self.app.current_year, self.app.current_month)[1]
        
        calendar_grid = CalendarGrid(
            self.scrollable_frame,
            self.app.current_year,
            self.app.current_month,
            self.app.current_employees,
            self.app.day_data,
            self.app.on_day_click,
            self.app.on_day_right_click
        )
        
        self.app.day_buttons = calendar_grid.create()
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def setup_employees_tab(self):
        """Настройка вкладки с сотрудниками"""
        button_frame = ttk.Frame(self.employees_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="➕ Добавить", 
                  command=self.app.add_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Редактировать", 
                  command=self.app.edit_employee_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Удалить", 
                  command=self.app.delete_employee).pack(side=tk.LEFT, padx=5)
        
        table_frame = ttk.Frame(self.employees_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ФИО', 'Должность', 'Ставка', 'Рабочие', 'Выходные', 'Отпуск', 'Больничный', 'Прочее')
        self.employees_tree = ttk.Treeview(table_frame, columns=columns, height=20, show='headings')
        
        widths = {'ФИО': 150, 'Должность': 150, 'Ставка': 70, 'Рабочие': 80, 
                 'Выходные': 80, 'Отпуск': 80, 'Больничный': 80, 'Прочее': 80}
        for col in columns:
            self.employees_tree.column(col, anchor=tk.CENTER, width=widths.get(col, 100))
            self.employees_tree.heading(col, text=col)
        
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.employees_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.employees_tree.xview)
        self.employees_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.employees_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.refresh_employees_tree()
    
    def refresh_employees_tree(self):
        """Обновление таблицы сотрудников (отсортированной по фамилиям)"""
        # Очистить старые строки
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        
        # Сортировка сотрудников по фамилии
        sorted_employees = sorted(self.app.current_employees, 
                                key=lambda e: e.get('name', '').split()[0] if e.get('name', '') else '')
        
        # Получаем текущий месяц
        month_key = self.app.get_month_key()
        
        # Добавить новые строки
        for emp in sorted_employees:
            # Получаем статистику за текущий месяц
            month_data = emp.get('months', {}).get(month_key, {})
            
            values = (
                emp.get('name', ''),
                emp.get('position', ''),
                f"{emp.get('rate', 1.0):.2f}",
                month_data.get('working_days', 0),
                month_data.get('weekends', 0),
                month_data.get('vacation', 0),
                month_data.get('sick_leave', 0),
                month_data.get('other', 0)
            )
            self.employees_tree.insert('', 'end', values=values)
    
    def get_selected_employee(self):
        """Получить выбранного сотрудника"""
        selection = self.employees_tree.selection()
        if not selection:
            from tkinter import messagebox
            messagebox.showwarning("Предупреждение", "Выберите сотрудника")
            return None
        
        emp_idx = self.employees_tree.index(selection[0])
        return emp_idx, self.app.current_employees[emp_idx]
    
    def setup_archive_tab(self):
        """Настройка вкладки архива"""
        button_frame = ttk.Frame(self.archive_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="💾 Сохранить текущий табель", 
                  command=self.app.save_current_to_archive).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📂 Загрузить", 
                  command=self.app.load_selected_from_archive).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Удалить", 
                  command=self.app.delete_selected_from_archive).pack(side=tk.LEFT, padx=5)
        
        table_frame = ttk.Frame(self.archive_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('Месяц', 'Год', 'Дата сохранения')
        self.archive_tree = ttk.Treeview(table_frame, columns=columns, height=20, show='headings')
        
        for col in columns:
            self.archive_tree.column(col, anchor=tk.CENTER, width=150)
            self.archive_tree.heading(col, text=col)
        
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.archive_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.archive_tree.xview)
        self.archive_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.archive_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.refresh_archive_list()
    
    def refresh_archive_list(self):
        """Обновить список архивов"""
        for item in self.archive_tree.get_children():
            self.archive_tree.delete(item)
        
        try:
            archive_dir = self.app.get_archive_dir()
            files = sorted([f for f in os.listdir(archive_dir) if f.endswith('.json')], reverse=True)
            
            for filename in files:
                filepath = os.path.join(archive_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        values = (
                            data.get('month_name', ''),
                            str(data.get('year', '')),
                            data.get('timestamp', '')
                        )
                        self.archive_tree.insert('', 'end', values=values, iid=filename)
                except:
                    pass
        except:
            pass
    
    def get_selected_archive(self):
        """Получить выбранный архив"""
        selected = self.archive_tree.selection()
        if not selected:
            from tkinter import messagebox
            messagebox.showwarning("Предупреждение", "Выберите табель для загрузки")
            return None
        return selected[0]
    
    def update_month_year_controls(self, month, year):
        """Обновить контролы месяца и года"""
        self.month_var.set(AppConfig.MONTHS[month - 1])
        self.year_var.set(str(year))
    
    def select_timetable_tab(self):
        """Переключиться на вкладку табеля"""
        self.notebook.select(0)
    
    def on_mousewheel(self, event):
        """Прокрутка мыши"""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def _add_tooltip(self, widget, text):
        """Добавить всплывающую подсказку"""
        tooltip_window = None
        
        def show_tooltip(event):
            nonlocal tooltip_window
            x = widget.winfo_rootx() + widget.winfo_width() // 2
            y = widget.winfo_rooty() + widget.winfo_height()
            
            tooltip_window = tk.Toplevel(widget)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(tooltip_window, text=text,
                        justify=tk.LEFT, background="#FFFFE0",
                        relief=tk.SOLID, borderwidth=1,
                        font=Fonts.TOOLTIP, padx=5, pady=3)
            label.pack()
        
        def hide_tooltip(event):
            nonlocal tooltip_window
            if tooltip_window:
                tooltip_window.destroy()
                tooltip_window = None
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)