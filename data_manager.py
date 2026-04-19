#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер данных для работы с сохранением и загрузкой информации о сотрудниках
Data Manager Module
"""

import json
import os
from pathlib import Path
from datetime import datetime


class DataManager:
    """Класс для управления данными приложения"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / 'data'
        self.employees_file = self.data_dir / 'employees.json'
        self.setup_data_dir()
    
    def setup_data_dir(self):
        """Создание директории для данных если её нет"""
        self.data_dir.mkdir(exist_ok=True)
    
    def load_employees(self):
        """Загрузка списка сотрудников из файла"""
        try:
            if self.employees_file.exists():
                with open(self.employees_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
        
        return self.get_default_employees()
    
    def save_employees(self, employees):
        """Сохранение списка сотрудников в файл"""
        try:
            with open(self.employees_file, 'w', encoding='utf-8') as f:
                json.dump(employees, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            return False
    
    def get_default_employees(self):
        """Получение списка сотрудников по умолчанию"""
        return [
            {
                'name': 'Иванов Иван Иванович',
                'position': 'Директор',
                'rate': 1.0,
                'working_days': 20,
                'weekends': 8,
                'vacation': 0,
                'sick_leave': 0,
                'other': 0,
                'day_data': '',
                'months': {}
            },
            {
                'name': 'Петров Петр Петрович',
                'position': 'Менеджер',
                'rate': 1.0,
                'working_days': 22,
                'weekends': 6,
                'vacation': 0,
                'sick_leave': 0,
                'other': 0,
                'day_data': '',
                'months': {}
            },
            {
                'name': 'Сидоров Сидор Сидорович',
                'position': 'Специалист',
                'rate': 0.5,
                'working_days': 20,
                'weekends': 8,
                'vacation': 0,
                'sick_leave': 1,
                'other': 0,
                'day_data': '',
                'months': {}
            }
        ]
    
    def get_employee_by_name(self, name):
        """Получение сотрудника по имени"""
        employees = self.load_employees()
        for emp in employees:
            if emp['name'] == name:
                return emp
        return None
    
    def update_employee(self, name, updated_data):
        """Обновление данных сотрудника"""
        employees = self.load_employees()
        for i, emp in enumerate(employees):
            if emp['name'] == name:
                employees[i].update(updated_data)
                self.save_employees(employees)
                return True
        return False
    
    def delete_employee(self, name):
        """Удаление сотрудника"""
        employees = self.load_employees()
        employees = [emp for emp in employees if emp['name'] != name]
        self.save_employees(employees)
    
    def add_employee(self, employee_data):
        """Добавление нового сотрудника"""
        employees = self.load_employees()
        employees.append(employee_data)
        self.save_employees(employees)
        return True
    
    def get_total_days(self, employee):
        """Подсчет общего количества дней"""
        return (
            employee.get('working_days', 0) +
            employee.get('weekends', 0) +
            employee.get('vacation', 0) +
            employee.get('sick_leave', 0) +
            employee.get('other', 0)
        )
    
    def export_month_data(self, month, year):
        """Получение данных за конкретный месяц"""
        employees = self.load_employees()
        
        # Добавляем информацию о месяце и году
        for emp in employees:
            emp['month'] = month
            emp['year'] = year
        
        return employees
