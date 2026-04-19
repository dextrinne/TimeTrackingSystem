#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Табель учета рабочего времени в календарном формате
Time tracking table in calendar format
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import calendar
import json
import os
from pathlib import Path
from template_exporter import TemplateExporter
from data_manager import DataManager


class TimeTableApp:
    """Главное приложение с табелем в календарном формате"""
    
    # Типы дней
    DAY_TYPES = {
        ' ': ('Пусто', 'white', ''),
        'Р': ('Рабочий день', '#90EE90', 'Р'),
        'В': ('Выходной', '#87CEEB', 'В'),
        'О': ('Отпуск', '#FFD700', 'О'),
        'Б': ('Больничный', '#FFB6C1', 'Б'),
        'П': ('Прочее', '#DDA0DD', 'П'),
    }
    
    DAY_TYPE_ORDER = [' ', 'Р', 'В', 'О', 'Б', 'П']
    
    def __init__(self, root):
        self.root = root
        self.root.title("Табель учета рабочего времени")
        self.root.geometry("1600x900")
        self.root.resizable(True, True)
        
        # Инициализация менеджеров
        self.data_manager = DataManager()
        self.exporter = TemplateExporter()
        
        # Текущие данные
        self.current_employees = []
        self.current_month = 1  # январь
        self.current_year = 2026
        self.day_buttons = {}  # { (employee_idx, day): button }
        self.day_data = {}  # { (employee_idx, day): type_code }
        
        # История для Ctrl+Z
        self.undo_stack = []  # Стек снимков состояния
        self.max_undo_depth = 50
        
        # Флаг для отложенного сохранения
        self.save_pending = False
        self.save_timer = None
        
        # Получить количество дней в месяце
        self.days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        
        # Сначала загружаем данные
        self.load_employees()
        self.load_day_data()
        
        # Потом строим интерфейс (когда данные уже загружены)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса с вкладками"""
        
        # Верхняя панель
        top_frame = ttk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="� Экспортировать в Excel", command=self.export_to_excel).pack(side=tk.LEFT, padx=5)
        ttk.Label(top_frame, text="💾 Автосохранение включено", foreground="green", font=("Arial", 9)).pack(side=tk.LEFT, padx=20)
        
        # Информация о типах дней
        info_frame = ttk.Frame(self.root)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        ttk.Label(info_frame, text="Типы: ", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        for code, (name, color, _) in self.DAY_TYPES.items():
            if code != ' ':
                btn = tk.Label(info_frame, text=name, bg=color, fg='black', padx=8, pady=2, relief=tk.RAISED)
                btn.pack(side=tk.LEFT, padx=3)
        
        ttk.Label(info_frame, text="    Левый клик: переключить тип  |  Правый клик: меню", 
                 foreground="blue", font=("Arial", 9)).pack(side=tk.LEFT, padx=20)
        
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
        
        # Привязка клавиш
        self.root.bind("<Control-z>", lambda e: self.on_undo())
        self.root.bind("<MouseWheel>", self.on_mousewheel)
        self.root.bind("<Button-4>", self.on_mousewheel)
        self.root.bind("<Button-5>", self.on_mousewheel)
    
    def setup_timetable_tab(self):
        """Настройка вкладки с табелем"""
        
        # Контроль месяца
        control_frame = ttk.Frame(self.timetable_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Месяц:").pack(side=tk.LEFT, padx=(0, 5))
        self.month_var = tk.StringVar(value='январь')
        months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
                 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
        month_combo = ttk.Combobox(control_frame, textvariable=self.month_var, 
                                   values=months, width=12, state='readonly')
        month_combo.pack(side=tk.LEFT, padx=5)
        month_combo.bind('<<ComboboxSelected>>', lambda e: self.on_month_changed())
        
        ttk.Label(control_frame, text="Год:").pack(side=tk.LEFT, padx=(20, 5))
        self.year_var = tk.StringVar(value='2026')
        year_spin = ttk.Spinbox(control_frame, from_=2020, to=2030, textvariable=self.year_var, 
                               command=self.on_year_changed, width=5)
        year_spin.pack(side=tk.LEFT, padx=5)
        
        # Canvas с прокруткой
        main_frame = ttk.Frame(self.timetable_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
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
    
    def setup_employees_tab(self):
        """Настройка вкладки с сотрудниками"""
        
        # Верхняя панель с кнопками
        button_frame = ttk.Frame(self.employees_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="➕ Добавить", command=self.add_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Редактировать", command=self.edit_employee_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Удалить", command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        
        # Таблица сотрудников
        table_frame = ttk.Frame(self.employees_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ФИО', 'Должность', 'Ставка', 'Рабочие', 'Выходные', 'Отпуск', 'Больничный', 'Прочее')
        self.employees_tree = ttk.Treeview(table_frame, columns=columns, height=20, show='headings')
        
        # Определение колонок
        widths = {'ФИО': 150, 'Должность': 150, 'Ставка': 70, 'Рабочие': 80, 'Выходные': 80, 'Отпуск': 80, 'Больничный': 80, 'Прочее': 80}
        for col in columns:
            self.employees_tree.column(col, anchor=tk.CENTER, width=widths.get(col, 100))
            self.employees_tree.heading(col, text=col)
        
        # Скролл-бары
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.employees_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.employees_tree.xview)
        self.employees_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.employees_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Загрузка сотрудников в таблицу
        self.refresh_employees_tree()
    
    def create_timetable(self):
        """Создание табеля с использованием grid для правильного выравнивания"""
        # Очищение старых элементов
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.day_buttons = {}
        
        # Получить количество дней
        self.days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        
        # Создание таблицы с grid
        # Заголовок: день месяца + день недели
        # Столбец 0: ФИО/должность
        # Столбцы 1+: дни месяца
        
        # Верхний заголовок (дни месяца и дни недели)
        header_label = tk.Label(self.scrollable_frame, text="ФИО / Должность", 
                               width=25, bg='#D3D3D3', fg='black', 
                               relief=tk.RIDGE, bd=1, font=("Arial", 9, "bold"))
        header_label.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        # Дни месяца в заголовке
        for day in range(1, self.days_in_month + 1):
            date_obj = datetime(self.current_year, self.current_month, day)
            day_name = date_obj.strftime("%a")[:2]  # Пн, Вт и т.д.
            
            # Цвет для выходных
            is_weekend = day_name in ['Сб', 'Вс']
            bg_color = '#E0E0E0' if is_weekend else 'white'
            
            day_label = tk.Label(self.scrollable_frame, 
                               text=f"{day}\n{day_name}", 
                               width=4, height=2,
                               bg=bg_color, fg='black',
                               relief=tk.RIDGE, bd=1,
                               font=("Arial", 8))
            day_label.grid(row=0, column=day, sticky="nsew", padx=1, pady=1)
        
        # Строки сотрудников
        for emp_idx, employee in enumerate(self.current_employees):
            row_num = emp_idx + 1
            
            # Колонка с ФИО и должностью (слева)
            name_text = f"{employee.get('name', '')}\n{employee.get('position', '')}"
            name_label = tk.Label(self.scrollable_frame, text=name_text,
                                 width=25, height=2, bg='#F0F0F0', fg='black',
                                 relief=tk.RIDGE, bd=1,
                                 anchor='nw', justify=tk.LEFT,
                                 font=("Arial", 9))
            name_label.grid(row=row_num, column=0, sticky="nsew", padx=1, pady=1)
            
            # Дни месяца для этого сотрудника (справа)
            for day in range(1, self.days_in_month + 1):
                day_key = (emp_idx, day)
                current_code = self.day_data.get(day_key, ' ')
                current_name, current_color, _ = self.DAY_TYPES[current_code]
                
                btn = tk.Label(self.scrollable_frame, 
                             text=current_code if current_code != ' ' else '',
                             width=4, height=2, bg=current_color, fg='black',
                             relief=tk.RAISED, bd=1, cursor="hand2",
                             font=("Arial", 10, "bold"))
                btn.grid(row=row_num, column=day, sticky="nsew", padx=1, pady=1)
                
                # Привязка клика
                btn.bind("<Button-1>", lambda e, key=day_key: self.on_day_click(key))
                btn.bind("<Button-3>", lambda e, key=day_key: self.on_day_right_click(key))
                
                self.day_buttons[day_key] = btn
        
        # Обновить scrollregion после построения таблицы
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_day_click(self, day_key):
        """Клик на день - переключить на следующий тип"""
        emp_idx, day = day_key
        current_code = self.day_data.get(day_key, ' ')
        
        # Найти следующий тип
        current_idx = self.DAY_TYPE_ORDER.index(current_code)
        next_idx = (current_idx + 1) % len(self.DAY_TYPE_ORDER)
        next_code = self.DAY_TYPE_ORDER[next_idx]
        
        # Не создавать undo если код не изменился
        if next_code != current_code:
            self.set_day_type(day_key, next_code)
    
    def on_day_right_click(self, day_key):
        """Правый клик на день - показать меню выбора"""
        emp_idx, day = day_key
        
        # Создание контекстного меню
        menu = tk.Menu(self.root, tearoff=0)
        
        for code, (name, _, _) in self.DAY_TYPES.items():
            menu.add_command(label=name, command=lambda c=code: self.set_day_type(day_key, c))
        
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()
    
    def set_day_type(self, day_key, code):
        """Установить тип дня"""
        # Проверить, что этот день существует
        emp_idx, day = day_key
        if emp_idx >= len(self.current_employees) or day > self.days_in_month:
            return
        
        # Сохранить в историю перед изменением
        self.push_undo_snapshot()
        
        self.day_data[day_key] = code
        
        # Обновить кнопку
        if day_key in self.day_buttons:
            name, color, _ = self.DAY_TYPES[code]
            btn = self.day_buttons[day_key]
            btn.config(bg=color, text=code if code != ' ' else '')
        
        self.schedule_autosave()
    
    def on_mousewheel(self, event):
        """Прокрутка мыши"""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
    
    def on_month_changed(self):
        """Смена месяца"""
        months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
                 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
        self.current_month = months.index(self.month_var.get()) + 1
        # Очистить undo при смене месяца
        self.undo_stack = []
        self.load_day_data()
        self.create_timetable()
    
    def on_year_changed(self):
        """Смена года"""
        try:
            self.current_year = int(self.year_var.get())
            # Очистить undo при смене года
            self.undo_stack = []
            self.load_day_data()
            self.create_timetable()
        except ValueError:
            pass
    
    def load_employees(self):
        """Загрузка сотрудников"""
        self.current_employees = self.data_manager.load_employees()
    
    def get_month_key(self):
        """Получить ключ месяца-года для сохранения (YYYY-MM)"""
        return f"{self.current_year}-{self.current_month:02d}"
    
    def load_day_data(self):
        """Загрузка данных дней для текущего месяца"""
        self.day_data = {}
        month_key = self.get_month_key()
        
        # Загрузить из сохраненных данных
        try:
            employees = self.data_manager.load_employees()
            for emp_idx, employee in enumerate(employees):
                # Ищем данные в словаре месяцев или в старом формате day_data
                if 'months' in employee and month_key in employee['months']:
                    day_string = employee['months'][month_key].get('day_data', '')
                elif 'day_data' in employee and employee['day_data'] and emp_idx < len(self.current_employees):
                    # Для совместимости с старым форматом
                    day_string = employee['day_data']
                else:
                    continue
                
                if not day_string:
                    continue
                    
                weeks = day_string.split('|')
                day_counter = 0
                for week in weeks:
                    for code in week:
                        day_counter += 1
                        if day_counter <= self.days_in_month:
                            key = (emp_idx, day_counter)
                            if code in self.DAY_TYPES:
                                self.day_data[key] = code
        except:
            pass
    
    def save_day_data(self):
        """Сохранение данных дней в сотрудников для текущего месяца"""
        month_key = self.get_month_key()
        employees = self.data_manager.load_employees()
        
        for emp_idx, employee in enumerate(employees):
            # Инициализировать структуру месяцев если её нет
            if 'months' not in employee:
                employee['months'] = {}
            
            # Инициализировать месяц если его нет
            if month_key not in employee['months']:
                employee['months'][month_key] = {
                    'working_days': 0,
                    'weekends': 0,
                    'vacation': 0,
                    'sick_leave': 0,
                    'other': 0,
                    'day_data': ''
                }
            
            # Собрать коды дней для этого сотрудника
            day_string = ""
            
            for day in range(1, self.days_in_month + 1):
                key = (emp_idx, day)
                code = self.day_data.get(key, ' ')
                day_string += code
                
                # Новая неделя каждые 7 дней
                if day % 7 == 0:
                    day_string += "|"
            
            if not day_string.endswith("|"):
                day_string += "|"
            
            employee['months'][month_key]['day_data'] = day_string
            
            # Пересчитать итоги для этого месяца
            counts = {}
            for day in range(1, self.days_in_month + 1):
                key = (emp_idx, day)
                code = self.day_data.get(key, ' ')
                if code == 'Р':
                    counts[1] = counts.get(1, 0) + 1
                elif code == 'В':
                    counts[2] = counts.get(2, 0) + 1
                elif code == 'О':
                    counts[3] = counts.get(3, 0) + 1
                elif code == 'Б':
                    counts[4] = counts.get(4, 0) + 1
                elif code == 'П':
                    counts[5] = counts.get(5, 0) + 1
            
            employee['months'][month_key]['working_days'] = counts.get(1, 0)
            employee['months'][month_key]['weekends'] = counts.get(2, 0)
            employee['months'][month_key]['vacation'] = counts.get(3, 0)
            employee['months'][month_key]['sick_leave'] = counts.get(4, 0)
            employee['months'][month_key]['other'] = counts.get(5, 0)
        
        self.data_manager.save_employees(employees)
        self.current_employees = employees
    
    def refresh_employees_tree(self):
        """Обновление таблицы сотрудников"""
        # Очистить старые строки
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        
        # Добавить новые строки
        for emp in self.current_employees:
            values = (
                emp.get('name', ''),
                emp.get('position', ''),
                f"{emp.get('rate', 1.0):.2f}",
                emp.get('working_days', 0),
                emp.get('weekends', 0),
                emp.get('vacation', 0),
                emp.get('sick_leave', 0),
                emp.get('other', 0)
            )
            self.employees_tree.insert('', 'end', values=values)
    
    def add_employee(self):
        """Добавление сотрудника"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить сотрудника")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="ФИО:").pack(anchor=tk.W, padx=20, pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(padx=20)
        
        ttk.Label(dialog, text="Должность:").pack(anchor=tk.W, padx=20, pady=5)
        position_entry = ttk.Entry(dialog, width=40)
        position_entry.pack(padx=20)
        
        ttk.Label(dialog, text="Ставка (0-1):").pack(anchor=tk.W, padx=20, pady=5)
        rate_entry = ttk.Entry(dialog, width=40)
        rate_entry.pack(padx=20)
        rate_entry.insert(0, "1.0")
        
        def save_emp():
            # Валидация: ФИО и должность обязательны
            if not name_entry.get().strip():
                messagebox.showwarning("Ошибка", "ФИО не может быть пусто")
                return
            if not position_entry.get().strip():
                messagebox.showwarning("Ошибка", "Должность не может быть пуста")
                return
            
            # Валидация ставки
            try:
                rate = float(rate_entry.get())
                if rate < 0 or rate > 1:
                    messagebox.showwarning("Ошибка", "Ставка должна быть от 0 до 1")
                    return
            except ValueError:
                messagebox.showwarning("Ошибка", "Ставка должна быть числом")
                return
            
            new_emp = {
                'name': name_entry.get().strip(),
                'position': position_entry.get().strip(),
                'rate': rate,
                'working_days': 0,
                'weekends': 0,
                'vacation': 0,
                'sick_leave': 0,
                'other': 0,
                'day_data': '',
                'months': {}
            }
            self.current_employees.append(new_emp)
            self.data_manager.save_employees(self.current_employees)
            self.refresh_employees_tree()
            self.load_day_data()
            self.create_timetable()
            dialog.destroy()
            messagebox.showinfo("Успешно", "Сотрудник добавлен!")
        
        ttk.Button(dialog, text="Сохранить", command=save_emp).pack(pady=10)
    
    def edit_employee_dialog(self):
        """Редактирование выбранного сотрудника"""
        selection = self.employees_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для редактирования")
            return
        
        emp_idx = self.employees_tree.index(selection[0])
        employee = self.current_employees[emp_idx]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать сотрудника")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="ФИО:").pack(anchor=tk.W, padx=20, pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(padx=20)
        name_entry.insert(0, employee.get('name', ''))
        
        ttk.Label(dialog, text="Должность:").pack(anchor=tk.W, padx=20, pady=5)
        position_entry = ttk.Entry(dialog, width=40)
        position_entry.pack(padx=20)
        position_entry.insert(0, employee.get('position', ''))
        
        ttk.Label(dialog, text="Ставка (0-1):").pack(anchor=tk.W, padx=20, pady=5)
        rate_entry = ttk.Entry(dialog, width=40)
        rate_entry.pack(padx=20)
        rate_entry.insert(0, str(employee.get('rate', 1.0)))
        
        def save_emp():
            # Валидация: ФИО и должность обязательны
            if not name_entry.get().strip():
                messagebox.showwarning("Ошибка", "ФИО не может быть пусто")
                return
            if not position_entry.get().strip():
                messagebox.showwarning("Ошибка", "Должность не может быть пуста")
                return
            
            # Валидация ставки
            try:
                rate = float(rate_entry.get())
                if rate < 0 or rate > 1:
                    messagebox.showwarning("Ошибка", "Ставка должна быть от 0 до 1")
                    return
            except ValueError:
                messagebox.showwarning("Ошибка", "Ставка должна быть числом")
                return
            
            self.push_undo_snapshot()
            employee['name'] = name_entry.get().strip()
            employee['position'] = position_entry.get().strip()
            employee['rate'] = rate
            self.data_manager.save_employees(self.current_employees)
            self.refresh_employees_tree()
            self.create_timetable()
            dialog.destroy()
            messagebox.showinfo("Успешно", "Данные сотрудника обновлены!")
        
        ttk.Button(dialog, text="Сохранить", command=save_emp).pack(pady=10)
    
    def delete_employee(self):
        """Удаление сотрудника"""
        selection = self.employees_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого сотрудника?"):
            emp_idx = self.employees_tree.index(selection[0])
            del self.current_employees[emp_idx]
            # Перестроить day_data после удаления сотрудника
            self.day_data = {}
            self.data_manager.save_employees(self.current_employees)
            self.refresh_employees_tree()
            self.load_day_data()
            self.create_timetable()
            messagebox.showinfo("Успешно", "Сотрудник удален!")
    
    def export_to_excel(self):
        """Экспорт в Excel"""
        if not self.current_employees:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xls",
            filetypes=[("Excel files", "*.xls"), ("All files", "*.*")],
            initialfile=f"табель-{self.month_var.get()}-{self.year_var.get()}.xls"
        )
        
        if file_path:
            try:
                months_list = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
                             'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
                month_name = months_list[self.current_month - 1]
                
                # Находим доступный шаблон
                template_candidates = [
                    'табель-январь2026.xls',
                    'табель-сентябрь2025.xls',
                    'табель-ноябрь2025.xls'
                ]
                
                template_path = None
                for candidate in template_candidates:
                    if os.path.exists(candidate):
                        template_path = candidate
                        break
                
                if not template_path:
                    messagebox.showerror("Ошибка", "Не найден шаблон табеля (.xls файл)")
                    return
                
                self.exporter.export_to_excel(
                    self.current_employees,
                    template_path,
                    file_path,
                    month_name,
                    self.current_year
                )
                messagebox.showinfo("Успешно", f"Файл сохранен: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    def push_undo_snapshot(self):
        """Сохранить текущее состояние в стек отмены"""
        # Снимок = копия день_дата для текущего месяца
        snapshot = {
            'day_data': dict(self.day_data),
            'employees': [dict(emp) for emp in self.current_employees]
        }
        self.undo_stack.append(snapshot)
        
        # Ограничить глубину стека
        if len(self.undo_stack) > self.max_undo_depth:
            self.undo_stack.pop(0)
    
    def schedule_autosave(self):
        """Запланировать автосохранение (2 сек задержка)"""
        # Отменить предыдущий таймер если существует
        if self.save_timer is not None:
            self.root.after_cancel(self.save_timer)
        
        # Запланировать новое сохранение
        self.save_timer = self.root.after(2000, self.save_day_data)
    
    def on_undo(self):
        """Отмена последнего действия (Ctrl+Z)"""
        if not self.undo_stack:
            return
        
        # Извлечь последний снимок
        snapshot = self.undo_stack.pop()
        self.day_data = snapshot['day_data']
        self.current_employees = snapshot['employees']
        
        # Перерисовать табель
        self.create_timetable()
        
        # Сразу сохранить восстановленное состояние
        if self.save_timer is not None:
            self.root.after_cancel(self.save_timer)
        self.save_day_data()
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        # Отменить таймер автосохранения если он есть
        if self.save_timer is not None:
            self.root.after_cancel(self.save_timer)
        
        self.save_day_data()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = TimeTableApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: app.on_closing())
    root.mainloop()

if __name__ == "__main__":
    main()
