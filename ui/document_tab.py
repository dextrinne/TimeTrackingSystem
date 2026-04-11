"""
Вкладка управления документами на tkinter.
ЛР1-Ф2: Ввод плановых неявок.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from database.models import Document
from services.document_service import DocumentService
from services.employee_service import EmployeeService
from utils.validators import Validator


class DocumentTab(ttk.Frame):
    """Вкладка документов."""

    def __init__(self, parent, db_manager, current_user):
        super().__init__(parent)
        self.db = db_manager
        self.current_user = current_user
        self.document_service = DocumentService(db_manager)
        self.employee_service = EmployeeService(db_manager)
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        # Панель действий
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(action_frame, text='➕ Добавить документ', command=self.add_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text='✏️ Редактировать', command=self.edit_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text='🗑️ Удалить', command=self.delete_document).pack(side=tk.LEFT, padx=5)

        # Таблица документов
        columns = ('id', 'employee_id', 'type', 'start_date', 'end_date')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        self.tree.heading('id', text='ID')
        self.tree.heading('employee_id', text='Сотрудник ID')
        self.tree.heading('type', text='Тип документа')
        self.tree.heading('start_date', text='Дата начала')
        self.tree.heading('end_date', text='Дата окончания')
        
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('employee_id', width=100, anchor=tk.CENTER)
        self.tree.column('type', width=200)
        self.tree.column('start_date', width=120, anchor=tk.CENTER)
        self.tree.column('end_date', width=120, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.load_documents()

    def load_documents(self):
        """Загрузка списка документов."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        documents = self.document_service.get_all_documents()
        for doc in documents:
            self.tree.insert('', tk.END, values=(
                doc.id_document, doc.employee_id, doc.type, doc.start_date, doc.end_date
            ))

    def get_selected_document_id(self):
        """Получить ID выбранного документа."""
        selection = self.tree.selection()
        if selection:
            return self.tree.item(selection[0])['values'][0]
        return None

    def add_document(self):
        """Добавление документа."""
        dialog = DocumentDialog(self, self.employee_service)
        self.wait_window(dialog)
        if dialog.result:
            document = dialog.get_document_data()
            is_valid, error = Validator.validate_dates(document.start_date, document.end_date)
            if is_valid:
                is_valid, error = Validator.validate_document_type(document.type)
                if is_valid:
                    self.document_service.add_document(document)
                    self.load_documents()
                    messagebox.showinfo('Успех', 'Документ добавлен')
                else:
                    messagebox.showwarning('Ошибка', error)
            else:
                messagebox.showwarning('Ошибка', error)

    def edit_document(self):
        """Редактирование документа."""
        document_id = self.get_selected_document_id()
        if not document_id:
            messagebox.showwarning('Ошибка', 'Выберите документ')
            return

        documents = self.document_service.get_all_documents()
        doc = next((d for d in documents if d.id_document == document_id), None)
        
        if doc:
            dialog = DocumentDialog(self, self.employee_service, doc)
            self.wait_window(dialog)
            if dialog.result:
                updated_doc = dialog.get_document_data()
                updated_doc.id_document = document_id
                is_valid, error = Validator.validate_dates(updated_doc.start_date, updated_doc.end_date)
                if is_valid:
                    self.document_service.update_document(updated_doc)
                    self.load_documents()
                    messagebox.showinfo('Успех', 'Документ обновлён')
                else:
                    messagebox.showwarning('Ошибка', error)

    def delete_document(self):
        """Удаление документа."""
        document_id = self.get_selected_document_id()
        if not document_id:
            messagebox.showwarning('Ошибка', 'Выберите документ')
            return

        if messagebox.askyesno('Удаление', 'Вы уверены, что хотите удалить этот документ?'):
            self.document_service.delete_document(document_id)
            self.load_documents()
            messagebox.showinfo('Успех', 'Документ удалён')


class DocumentDialog(tk.Toplevel):
    """Диалог ввода/редактирования документа."""

    def __init__(self, parent, employee_service, document=None):
        super().__init__(parent)
        self.employee_service = employee_service
        self.document = document
        self.result = False
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        self.title('Добавление документа' if not self.document else 'Редактирование документа')
        self.geometry('400x300')
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()

        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Выбор сотрудника
        ttk.Label(form_frame, text='Сотрудник:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.employee_combo = ttk.Combobox(form_frame, state='readonly', width=32)
        employees = self.employee_service.get_all_employees()
        self.employee_map = {emp.fio: emp.id_employee for emp in employees}
        self.employee_combo['values'] = list(self.employee_map.keys())
        if self.document:
            for fio, emp_id in self.employee_map.items():
                if emp_id == self.document.employee_id:
                    self.employee_combo.set(fio)
                    break
        self.employee_combo.grid(row=0, column=1, pady=5)

        # Тип документа
        ttk.Label(form_frame, text='Тип документа:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value=self.document.type if self.document else 'Отпуск')
        type_combo = ttk.Combobox(form_frame, textvariable=self.type_var,
                                  values=['Отпуск', 'Больничный', 'Командировка', 'Отгул'],
                                  state='readonly', width=32)
        type_combo.grid(row=1, column=1, pady=5)

        # Даты
        ttk.Label(form_frame, text='Дата начала\n(ГГГГ-ММ-ДД):').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar(value=self.document.start_date.isoformat() if self.document else date.today().isoformat())
        ttk.Entry(form_frame, textvariable=self.start_date_var, width=15).grid(row=2, column=1, pady=5, sticky=tk.W)

        ttk.Label(form_frame, text='Дата окончания\n(ГГГГ-ММ-ДД):').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.end_date_var = tk.StringVar(value=self.document.end_date.isoformat() if self.document else date.today().isoformat())
        ttk.Entry(form_frame, textvariable=self.end_date_var, width=15).grid(row=3, column=1, pady=5, sticky=tk.W)

        # Кнопки
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(button_frame, text='💾 Сохранить', command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='❌ Отмена', command=self.destroy).pack(side=tk.LEFT, padx=5)

    def save(self):
        """Сохранение данных."""
        self.result = True
        self.destroy()

    def get_document_data(self):
        """Получить данные документа."""
        document = Document()
        selected_fio = self.employee_combo.get()
        document.employee_id = self.employee_map.get(selected_fio, 0)
        document.type = self.type_var.get()
        document.start_date = datetime.strptime(self.start_date_var.get(), '%Y-%m-%d').date()
        document.end_date = datetime.strptime(self.end_date_var.get(), '%Y-%m-%d').date()
        return document
