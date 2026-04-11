"""
Вкладка управления табелями на tkinter.
ЛР1-Ф3: Формирование электронного табеля.
ЛР2: Автоматический расчёт, управление статусами.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from database.models import Timesheet, TimesheetEntry
from services.timesheet_service import TimesheetService
from services.employee_service import EmployeeService


class TimesheetTab(ttk.Frame):
    """Вкладка табелей."""

    def __init__(self, parent, db_manager, current_user):
        super().__init__(parent)
        self.db = db_manager
        self.current_user = current_user
        self.timesheet_service = TimesheetService(db_manager)
        self.employee_service = EmployeeService(db_manager)
        self.current_timesheet_id = None
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        # Панель действий
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(action_frame, text='➕ Создать табель', command=self.create_timesheet).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(action_frame, text='Статус:').pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value='В работе')
        status_combo = ttk.Combobox(action_frame, textvariable=self.status_var, 
                                     values=['В работе', 'Утверждён', 'Архивирован'], 
                                     state='readonly', width=15)
        status_combo.pack(side=tk.LEFT, padx=5)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.change_status())

        ttk.Button(action_frame, text='🔄 Сформировать дни', command=self.generate_days).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text='📊 Подсчитать итоги', command=self.calculate_totals).pack(side=tk.LEFT, padx=5)

        # Разделитель
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=5)

        # Список табелей
        list_frame = ttk.LabelFrame(self, text='Табели')
        list_frame.pack(fill=tk.X, padx=5, pady=5)

        columns = ('id', 'period', 'status', 'created')
        self.timesheet_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=5)
        
        self.timesheet_tree.heading('id', text='ID')
        self.timesheet_tree.heading('period', text='Период')
        self.timesheet_tree.heading('status', text='Статус')
        self.timesheet_tree.heading('created', text='Создан')
        
        self.timesheet_tree.column('id', width=50, anchor=tk.CENTER)
        self.timesheet_tree.column('period', width=200)
        self.timesheet_tree.column('status', width=120, anchor=tk.CENTER)
        self.timesheet_tree.column('created', width=150)

        self.timesheet_tree.bind('<<TreeviewSelect>>', self.on_timesheet_selected)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.timesheet_tree.yview)
        self.timesheet_tree.configure(yscrollcommand=scrollbar.set)
        
        self.timesheet_tree.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Записи табеля
        entries_frame = ttk.LabelFrame(self, text='Записи табеля')
        entries_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        entry_columns = ('id', 'employee_id', 'date', 'hours', 'type')
        self.entries_tree = ttk.Treeview(entries_frame, columns=entry_columns, show='headings')
        
        self.entries_tree.heading('id', text='ID')
        self.entries_tree.heading('employee_id', text='Сотрудник ID')
        self.entries_tree.heading('date', text='Дата')
        self.entries_tree.heading('hours', text='Часы')
        self.entries_tree.heading('type', text='Тип')
        
        self.entries_tree.column('id', width=50, anchor=tk.CENTER)
        self.entries_tree.column('employee_id', width=80, anchor=tk.CENTER)
        self.entries_tree.column('date', width=100, anchor=tk.CENTER)
        self.entries_tree.column('hours', width=70, anchor=tk.CENTER)
        self.entries_tree.column('type', width=150)

        entry_scrollbar = ttk.Scrollbar(entries_frame, orient=tk.VERTICAL, command=self.entries_tree.yview)
        self.entries_tree.configure(yscrollcommand=entry_scrollbar.set)
        
        self.entries_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        entry_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.load_timesheets()

    def load_timesheets(self):
        """Загрузка списка табелей."""
        for item in self.timesheet_tree.get_children():
            self.timesheet_tree.delete(item)
        
        timesheets = self.timesheet_service.get_all_timesheets()
        for ts in timesheets:
            self.timesheet_tree.insert('', tk.END, values=(
                ts.id_timesheet,
                f"{ts.period_start} — {ts.period_end}",
                ts.status,
                ts.created_at
            ))

    def on_timesheet_selected(self, event):
        """Обработка выбора табеля."""
        selection = self.timesheet_tree.selection()
        if selection:
            self.current_timesheet_id = self.timesheet_tree.item(selection[0])['values'][0]
            status = self.timesheet_tree.item(selection[0])['values'][2]
            self.status_var.set(status)
            self.load_entries()

    def load_entries(self):
        """Загрузка записей выбранного табеля."""
        if not self.current_timesheet_id:
            return

        for item in self.entries_tree.get_children():
            self.entries_tree.delete(item)

        entries = self.timesheet_service.get_entries_by_timesheet(self.current_timesheet_id)
        for entry in entries:
            self.entries_tree.insert('', tk.END, values=(
                entry.id_timesheet_entry,
                entry.employee_id,
                entry.date,
                entry.hours_worked,
                entry.type
            ))

    def create_timesheet(self):
        """Создание нового табеля."""
        dialog = CreateTimesheetDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            period_start, period_end = dialog.get_period()
            timesheet_id = self.timesheet_service.create_timesheet(period_start, period_end)
            if timesheet_id:
                self.load_timesheets()
                messagebox.showinfo('Успех', 'Табель создан')
            else:
                messagebox.showwarning('Ошибка', 'Не удалось создать табель')

    def change_status(self):
        """Изменение статуса табеля."""
        if not self.current_timesheet_id:
            messagebox.showwarning('Ошибка', 'Выберите табель')
            return

        status = self.status_var.get()
        self.timesheet_service.update_timesheet_status(self.current_timesheet_id, status)
        self.load_timesheets()
        messagebox.showinfo('Успех', f'Статус изменён на "{status}"')

    def generate_days(self):
        """Автоматическое формирование дней."""
        if not self.current_timesheet_id:
            messagebox.showwarning('Ошибка', 'Выберите табель')
            return

        employees = self.employee_service.get_all_employees()
        if not employees:
            messagebox.showwarning('Ошибка', 'Нет сотрудников в базе')
            return

        employee_ids = [emp.id_employee for emp in employees]
        self.timesheet_service.generate_timesheet_structure(self.current_timesheet_id, employee_ids)
        self.load_entries()
        messagebox.showinfo('Успех', 'Структура табеля сформирована')

    def calculate_totals(self):
        """Подсчёт итогов."""
        if not self.current_timesheet_id:
            messagebox.showwarning('Ошибка', 'Выберите табель')
            return

        employees = self.employee_service.get_all_employees()
        totals_text = "ИТОГИ ПО ТАБЕЛЯМ:\n\n"
        
        for emp in employees:
            totals = self.timesheet_service.calculate_employee_totals(emp.id_employee, self.current_timesheet_id)
            totals_text += f"{emp.fio}:\n"
            totals_text += f"  Рабочих дней: {totals['workdays']}\n"
            totals_text += f"  Всего часов: {totals['total_hours']}\n"
            totals_text += f"  Отпуск: {totals['vacations']} дн.\n"
            totals_text += f"  Больничный: {totals['sick_leaves']} дн.\n\n"

        messagebox.showinfo('Итоги', totals_text)


class CreateTimesheetDialog(tk.Toplevel):
    """Диалог создания табеля."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.result = False
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        self.title('Создание табеля')
        self.geometry('350x200')
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()

        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(form_frame, text='Дата начала\n(ГГГГ-ММ-ДД):').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar(value=(date.today().replace(month=date.today().month - 1 if date.today().month > 1 else 12)).isoformat())
        ttk.Entry(form_frame, textvariable=self.start_date_var, width=15).grid(row=0, column=1, pady=5, sticky=tk.W)

        ttk.Label(form_frame, text='Дата окончания\n(ГГГГ-ММ-ДД):').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(form_frame, textvariable=self.end_date_var, width=15).grid(row=1, column=1, pady=5, sticky=tk.W)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(button_frame, text='✅ Создать', command=self.create).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='❌ Отмена', command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def create(self):
        """Создание табеля."""
        self.result = True
        self.destroy()
    
    def get_period(self):
        start = datetime.strptime(self.start_date_var.get(), '%Y-%m-%d').date()
        end = datetime.strptime(self.end_date_var.get(), '%Y-%m-%d').date()
        return start, end
