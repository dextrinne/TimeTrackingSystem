"""
Вкладка управления сотрудниками на tkinter.
ЛР1-Ф1: Ведение справочной информации о сотрудниках.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.models import Employee
from services.employee_service import EmployeeService
from utils.validators import Validator


class EmployeeTab(ttk.Frame):
    """Вкладка сотрудников."""

    def __init__(self, parent, db_manager, current_user):
        super().__init__(parent)
        self.db = db_manager
        self.current_user = current_user
        self.service = EmployeeService(db_manager)
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        # Панель действий
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(action_frame, text='Поиск:').pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_employees())
        ttk.Entry(action_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)

        ttk.Button(action_frame, text='➕ Добавить', command=self.add_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text='✏️ Редактировать', command=self.edit_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text='🗑️ Удалить', command=self.delete_employee).pack(side=tk.LEFT, padx=5)

        # Таблица сотрудников
        columns = ('id', 'fio', 'position', 'rate', 'norm_hours')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        self.tree.heading('id', text='ID')
        self.tree.heading('fio', text='ФИО')
        self.tree.heading('position', text='Должность')
        self.tree.heading('rate', text='Ставка')
        self.tree.heading('norm_hours', text='Норма часов')
        
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('fio', width=300)
        self.tree.column('position', width=200)
        self.tree.column('rate', width=80, anchor=tk.CENTER)
        self.tree.column('norm_hours', width=100, anchor=tk.CENTER)

        # Скроллбар
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.load_employees()

    def load_employees(self):
        """Загрузка списка сотрудников."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        employees = self.service.get_all_employees()
        for emp in employees:
            self.tree.insert('', tk.END, values=(
                emp.id_employee, emp.fio, emp.position, emp.rate, emp.norm_hours
            ))

    def search_employees(self):
        """Поиск сотрудников."""
        search_term = self.search_var.get()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if search_term:
            employees = self.service.search_employees(search_term)
        else:
            employees = self.service.get_all_employees()
        
        for emp in employees:
            self.tree.insert('', tk.END, values=(
                emp.id_employee, emp.fio, emp.position, emp.rate, emp.norm_hours
            ))

    def get_selected_employee_id(self):
        """Получить ID выбранного сотрудника."""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0])['values'][0]
        return None

    def add_employee(self):
        """Добавление сотрудника."""
        dialog = EmployeeDialog(self, self.service)
        self.wait_window(dialog)
        if dialog.result:
            employee = dialog.get_employee_data()
            is_valid, error = Validator.validate_employee_data(
                employee.fio, employee.position, employee.rate, employee.norm_hours
            )
            if is_valid:
                self.service.add_employee(employee)
                self.load_employees()
                messagebox.showinfo('Успех', 'Сотрудник добавлен')
            else:
                messagebox.showwarning('Ошибка', error)

    def edit_employee(self):
        """Редактирование сотрудника."""
        employee_id = self.get_selected_employee_id()
        if not employee_id:
            messagebox.showwarning('Ошибка', 'Выберите сотрудника')
            return

        employee = self.service.get_employee_by_id(employee_id)
        if employee:
            dialog = EmployeeDialog(self, self.service, employee)
            self.wait_window(dialog)
            if dialog.result:
                updated_employee = dialog.get_employee_data()
                updated_employee.id_employee = employee_id
                is_valid, error = Validator.validate_employee_data(
                    updated_employee.fio, updated_employee.position, 
                    updated_employee.rate, updated_employee.norm_hours
                )
                if is_valid:
                    self.service.update_employee(updated_employee)
                    self.load_employees()
                    messagebox.showinfo('Успех', 'Данные обновлены')
                else:
                    messagebox.showwarning('Ошибка', error)

    def delete_employee(self):
        """Удаление сотрудника."""
        employee_id = self.get_selected_employee_id()
        if not employee_id:
            messagebox.showwarning('Ошибка', 'Выберите сотрудника')
            return

        if messagebox.askyesno('Удаление', 'Вы уверены, что хотите удалить этого сотрудника?'):
            self.service.delete_employee(employee_id)
            self.load_employees()
            messagebox.showinfo('Успех', 'Сотрудник удалён')


class EmployeeDialog(tk.Toplevel):
    """Диалог ввода/редактирования сотрудника."""

    def __init__(self, parent, service, employee=None):
        super().__init__(parent)
        self.service = service
        self.employee = employee
        self.result = False
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        self.title('Добавление сотрудника' if not self.employee else 'Редактирование сотрудника')
        self.geometry('400x300')
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()

        # Поля формы
        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(form_frame, text='ФИО:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.fio_var = tk.StringVar(value=self.employee.fio if self.employee else '')
        ttk.Entry(form_frame, textvariable=self.fio_var, width=35).grid(row=0, column=1, pady=5)

        ttk.Label(form_frame, text='Должность:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.position_var = tk.StringVar(value=self.employee.position if self.employee else '')
        ttk.Entry(form_frame, textvariable=self.position_var, width=35).grid(row=1, column=1, pady=5)

        ttk.Label(form_frame, text='Ставка:').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.rate_var = tk.DoubleVar(value=self.employee.rate if self.employee else 1.0)
        ttk.Spinbox(form_frame, from_=0, to=999.99, increment=0.25, textvariable=self.rate_var, width=10).grid(row=2, column=1, pady=5, sticky=tk.W)

        ttk.Label(form_frame, text='Норма часов:').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.norm_hours_var = tk.IntVar(value=self.employee.norm_hours if self.employee else 40)
        ttk.Spinbox(form_frame, from_=0, to=168, textvariable=self.norm_hours_var, width=10).grid(row=3, column=1, pady=5, sticky=tk.W)

        # Кнопки
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(button_frame, text='💾 Сохранить', command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='❌ Отмена', command=self.destroy).pack(side=tk.LEFT, padx=5)

    def save(self):
        """Сохранение данных."""
        self.result = True
        self.destroy()

    def get_employee_data(self):
        """Получить данные сотрудника."""
        employee = Employee()
        employee.fio = self.fio_var.get()
        employee.position = self.position_var.get()
        employee.rate = self.rate_var.get()
        employee.norm_hours = self.norm_hours_var.get()
        return employee
