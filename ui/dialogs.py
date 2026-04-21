# Диалоговые окна приложения
import tkinter as tk
from tkinter import ttk, messagebox


class EmployeeDialog:
    """Диалог добавления/редактирования сотрудника"""
    
    def __init__(self, parent, title, employee=None):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets(employee)
        
        # Ждем закрытия диалога
        parent.wait_window(self.dialog)
    
    def _create_widgets(self, employee):
        """Создание виджетов диалога"""
        ttk.Label(self.dialog, text="ФИО:").pack(anchor=tk.W, padx=20, pady=5)
        self.name_entry = ttk.Entry(self.dialog, width=40)
        self.name_entry.pack(padx=20)
        
        ttk.Label(self.dialog, text="Должность:").pack(anchor=tk.W, padx=20, pady=5)
        self.position_entry = ttk.Entry(self.dialog, width=40)
        self.position_entry.pack(padx=20)
        
        ttk.Label(self.dialog, text="Ставка (0-1):").pack(anchor=tk.W, padx=20, pady=5)
        self.rate_entry = ttk.Entry(self.dialog, width=40)
        self.rate_entry.pack(padx=20)
        
        if employee:
            self.name_entry.insert(0, employee.get('name', ''))
            self.position_entry.insert(0, employee.get('position', ''))
            self.rate_entry.insert(0, str(employee.get('rate', 1.0)))
        else:
            self.rate_entry.insert(0, "1.0")
        
        ttk.Button(self.dialog, text="Сохранить", command=self._save).pack(pady=10)
    
    def _save(self):
        """Сохранение данных"""
        name = self.name_entry.get().strip()
        position = self.position_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Ошибка", "ФИО не может быть пусто")
            return
        if not position:
            messagebox.showwarning("Ошибка", "Должность не может быть пуста")
            return
        
        try:
            rate = float(self.rate_entry.get())
            if rate < 0 or rate > 1:
                messagebox.showwarning("Ошибка", "Ставка должна быть от 0 до 1")
                return
        except ValueError:
            messagebox.showwarning("Ошибка", "Ставка должна быть числом")
            return
        
        self.result = {
            'name': name,
            'position': position,
            'rate': rate
        }
        self.dialog.destroy()