import json
import os
from pathlib import Path
from frontend.config import AppConfig

class DataManager:
    def __init__(self):
        self.employees_file = AppConfig.EMPLOYEES_FILE
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """Проверка наличия файла данных"""
        if not self.employees_file.exists():
            self.save_employees([])
    
    def load_employees(self):
        """Загрузка списка сотрудников"""
        try:
            with open(self.employees_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_employees(self, employees):
        """Сохранение списка сотрудников"""
        with open(self.employees_file, 'w', encoding='utf-8') as f:
            json.dump(employees, f, ensure_ascii=False, indent=2)
    
    def get_employee(self, index):
        """Получить сотрудника по индексу"""
        employees = self.load_employees()
        if 0 <= index < len(employees):
            return employees[index]
        return None
    
    def add_employee(self, employee_data):
        """Добавление сотрудника"""
        employees = self.load_employees()
        employees.append(employee_data)
        self.save_employees(employees)
    
    def update_employee(self, index, employee_data):
        """Обновление данных сотрудника"""
        employees = self.load_employees()
        if 0 <= index < len(employees):
            employees[index] = employee_data
            self.save_employees(employees)
    
    def delete_employee(self, index):
        """Удаление сотрудника"""
        employees = self.load_employees()
        if 0 <= index < len(employees):
            del employees[index]
            self.save_employees(employees)