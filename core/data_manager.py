import json
import os
from pathlib import Path
from frontend.config import AppConfig

class DataManager:
    def __init__(self):
        self.employees_file = AppConfig.EMPLOYEES_FILE
        self.ensure_data_file()
    
    # Проверка наличия файла данных
    def ensure_data_file(self):
        if not self.employees_file.exists():
            self.save_employees([])
    
    # Загрузка списка сотрудников
    def load_employees(self):
        try:
            with open(self.employees_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    # Сохранение списка сотрудников
    def save_employees(self, employees):
        with open(self.employees_file, 'w', encoding='utf-8') as f:
            json.dump(employees, f, ensure_ascii=False, indent=2)
    
    # Получить сотрудника по индексу
    def get_employee(self, index):
        employees = self.load_employees()
        if 0 <= index < len(employees):
            return employees[index]
        return None
    
    # Добавление сотрудника
    def add_employee(self, employee_data):
        employees = self.load_employees()
        employees.append(employee_data)
        self.save_employees(employees)
    
    # Обновление данных сотрудника
    def update_employee(self, index, employee_data):
        employees = self.load_employees()
        if 0 <= index < len(employees):
            employees[index] = employee_data
            self.save_employees(employees)
    
    # Удаление сотрудника
    def delete_employee(self, index):
        employees = self.load_employees()
        if 0 <= index < len(employees):
            del employees[index]
            self.save_employees(employees)