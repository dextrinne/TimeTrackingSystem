import tkinter as tk
from datetime import datetime
from frontend.styles import DayTypes, Colors, Fonts


class CalendarGrid:
    """Календарная сетка табеля"""
    
    def __init__(self, parent, year, month, employees, day_data, 
                 on_click, on_right_click):
        self.parent = parent
        self.year = year
        self.month = month
        self.employees = employees
        self.day_data = day_data
        self.on_click = on_click
        self.on_right_click = on_right_click
        self.day_buttons = {}
        self.tooltip_window = None
    
    def _create_day_button(self, emp_idx, day, row_num):
        """Создание кнопки дня с тултипом"""
        day_key = (emp_idx, day)
        current_code = self.day_data.get(day_key, DayTypes.EMPTY)
        current_name, current_color, short_code = DayTypes.TYPES[current_code]
        
        # Определяем текст на кнопке
        button_text = short_code if short_code else ''
        
        # Для длинных кодов уменьшаем шрифт
        font = Fonts.DAY_BUTTON
        if len(button_text) > 2:
            font = ("Arial", 8, "bold")
        
        btn = tk.Label(self.parent, 
                     text=button_text,
                     width=4, height=2, bg=current_color, fg=Colors.TEXT,
                     relief=tk.RAISED, bd=1, cursor="hand2",
                     font=font)
        btn.grid(row=row_num, column=day, sticky="nsew", padx=1, pady=1)
        
        btn.bind("<Button-1>", lambda e, key=day_key: self.on_click(key))
        btn.bind("<Button-3>", lambda e, key=day_key: self.on_right_click(key))
        
        # Добавляем тултип с полным названием
        self._add_tooltip(btn, current_name, day_key)
        
        self.day_buttons[day_key] = btn
    
    def _add_tooltip(self, widget, text, day_key=None):
        """Добавить всплывающую подсказку к виджету"""
        def show_tooltip(event):
            x = widget.winfo_rootx() + widget.winfo_width() // 2
            y = widget.winfo_rooty() + widget.winfo_height()
            
            self.tooltip_window = tk.Toplevel(widget)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
            
            # Добавляем информацию о дне если есть day_key
            if day_key:
                emp_idx, day = day_key
                employee = self.employees[emp_idx]
                date_obj = datetime(self.year, self.month, day)
                date_str = date_obj.strftime("%d.%m.%Y")
                
                tooltip_text = f"{text}\n{employee.get('name', '')}\n{date_str}"
            else:
                tooltip_text = text
            
            label = tk.Label(self.tooltip_window, text=tooltip_text,
                           justify=tk.LEFT, background="#FFFFE0",
                           relief=tk.SOLID, borderwidth=1,
                           font=Fonts.TOOLTIP, padx=5, pady=3)
            label.pack()
        
        def hide_tooltip(event):
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def create(self):
        """Создание календарной сетки с учетом сортировки сотрудников"""
        days_in_month = self._get_days_in_month()
        
        # Заголовок ФИО/Должность
        header_label = tk.Label(self.parent, text="ФИО / Должность", 
                            width=25, bg=Colors.HEADER_BG, fg=Colors.TEXT, 
                            relief=tk.RIDGE, bd=1, font=Fonts.HEADER)
        header_label.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        # Дни месяца в заголовке
        for day in range(1, days_in_month + 1):
            self._create_day_header(day, 0, day)
        
        # Строки сотрудников (уже отсортированы)
        for emp_idx, employee in enumerate(self.employees):
            row_num = emp_idx + 1
            self._create_employee_row(emp_idx, employee, row_num, days_in_month)
        
        return self.day_buttons
    
    def _get_days_in_month(self):
        """Получить количество дней в месяце"""
        import calendar
        return calendar.monthrange(self.year, self.month)[1]
    
    def _create_day_header(self, day, row, column):
        """Создание заголовка дня"""
        date_obj = datetime(self.year, self.month, day)
        day_name = date_obj.strftime("%a")[:2]
        
        is_weekend = day_name in ['Сб', 'Вс']
        bg_color = Colors.WEEKEND_HEADER if is_weekend else Colors.WHITE
        
        day_label = tk.Label(self.parent, 
                           text=f"{day}\n{day_name}", 
                           width=4, height=2,
                           bg=bg_color, fg=Colors.TEXT,
                           relief=tk.RIDGE, bd=1,
                           font=("Arial", 8))
        day_label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
    
    def _create_employee_row(self, emp_idx, employee, row_num, days_in_month):
        """Создание строки сотрудника"""
        # Колонка с ФИО и должностью
        name_text = f"{employee.get('name', '')}\n{employee.get('position', '')}"
        name_label = tk.Label(self.parent, text=name_text,
                             width=25, height=2, bg=Colors.EMPLOYEE_BG, fg=Colors.TEXT,
                             relief=tk.RIDGE, bd=1,
                             anchor='nw', justify=tk.LEFT,
                             font=("Arial", 9))
        name_label.grid(row=row_num, column=0, sticky="nsew", padx=1, pady=1)
        
        # Дни месяца
        for day in range(1, days_in_month + 1):
            self._create_day_button(emp_idx, day, row_num)
    
    def _create_day_button(self, emp_idx, day, row_num):
        """Создание кнопки дня"""
        day_key = (emp_idx, day)
        current_code = self.day_data.get(day_key, DayTypes.EMPTY)
        current_name, current_color, _ = DayTypes.TYPES[current_code]
        
        btn = tk.Label(self.parent, 
                     text=current_code if current_code != DayTypes.EMPTY else '',
                     width=4, height=2, bg=current_color, fg=Colors.TEXT,
                     relief=tk.RAISED, bd=1, cursor="hand2",
                     font=("Arial", 10, "bold"))
        btn.grid(row=row_num, column=day, sticky="nsew", padx=1, pady=1)
        
        btn.bind("<Button-1>", lambda e, key=day_key: self.on_click(key))
        btn.bind("<Button-3>", lambda e, key=day_key: self.on_right_click(key))
        
        self.day_buttons[day_key] = btn


class DayButton(tk.Label):
    """Кастомная кнопка для дня в табеле"""
    
    def __init__(self, parent, day_key, code, on_click, on_right_click, **kwargs):
        super().__init__(parent, **kwargs)
        self.day_key = day_key
        self.code = code
        
        self.bind("<Button-1>", lambda e: on_click(day_key))
        self.bind("<Button-3>", lambda e: on_right_click(day_key))
        
        self._update_style()
    
    def _update_style(self):
        """Обновление стиля кнопки"""
        name, color, text = DayTypes.TYPES[self.code]
        self.config(bg=color, text=text if self.code != DayTypes.EMPTY else '')
    
    def set_code(self, code):
        """Установка нового кода дня"""
        self.code = code
        self._update_style()