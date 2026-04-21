#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер данных для работы с сотрудниками
"""

import json
import os
from pathlib import Path


class DataManager:
    """Управление загрузкой и сохранением данных сотрудников"""
    
    def __init__(self, data_file=None):
        """
        Инициализация менеджера данных
        
        Args:
            data_file: путь к файлу с данными (по умолчанию data/employees.json)
        """
        if data_file is None:
            # По умолчанию используем data/employees.json
            self.data_file = self._get_default_data_file()
        else:
            self.data_file = data_file
        
        # Создаем директорию data если её нет
        self._ensure_data_dir()
    
    def _get_default_data_file(self):
        """Получить путь к файлу данных по умолчанию"""
        # Определяем корневую директорию проекта
        current_dir = Path(__file__).parent.parent
        data_dir = current_dir / 'data'
        return str(data_dir / 'employees.json')
    
    def _ensure_data_dir(self):
        """Создать директорию data если её нет"""
        data_dir = Path(self.data_file).parent
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_employees(self):
        """
        Загрузка списка сотрудников из JSON файла
        
        Returns:
            list: список сотрудников
        """
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    employees = json.load(f)
                    
                    # Проверяем и инициализируем обязательные поля
                    for emp in employees:
                        self._ensure_employee_structure(emp)
                    
                    return employees
            else:
                # Если файла нет, создаем пустой список и сохраняем
                empty_list = []
                self.save_employees(empty_list)
                return empty_list
                
        except json.JSONDecodeError as e:
            print(f"Ошибка чтения JSON: {e}")
            # Создаем резервную копию поврежденного файла
            self._backup_corrupted_file()
            return []
        except Exception as e:
            print(f"Ошибка загрузки сотрудников: {e}")
            return []
    
    def _ensure_employee_structure(self, employee):
        """
        Проверить и инициализировать структуру сотрудника
        
        Args:
            employee: словарь с данными сотрудника
        """
        # Обязательные поля
        if 'name' not in employee:
            employee['name'] = ''
        if 'position' not in employee:
            employee['position'] = ''
        if 'rate' not in employee:
            employee['rate'] = 1.0
        
        # Статистика
        if 'working_days' not in employee:
            employee['working_days'] = 0
        if 'weekends' not in employee:
            employee['weekends'] = 0
        if 'vacation' not in employee:
            employee['vacation'] = 0
        if 'sick_leave' not in employee:
            employee['sick_leave'] = 0
        if 'other' not in employee:
            employee['other'] = 0
        
        # Данные дней
        if 'day_data' not in employee:
            employee['day_data'] = ''
        
        # Месяцы
        if 'months' not in employee:
            employee['months'] = {}
    
    def save_employees(self, employees):
        """
        Сохранение списка сотрудников в JSON файл с автоматической сортировкой
        
        Args:
            employees: список сотрудников для сохранения
        """
        try:
            # Сортируем сотрудников перед сохранением
            sorted_employees = sorted(
                employees,
                key=lambda e: self._get_sort_key(e.get('name', ''))
            )
            
            # Создаем директорию если её нет
            self._ensure_data_dir()
            
            # Сохраняем с форматированием
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(sorted_employees, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            print(f"Ошибка сохранения сотрудников: {e}")
            raise

    def _get_sort_key(self, full_name):
        """Получить ключ для сортировки по фамилии"""
        if not full_name:
            return ''
        
        parts = full_name.split()
        if parts:
            return parts[0].lower()
        return full_name.lower()
    
    def _backup_corrupted_file(self):
        """Создать резервную копию поврежденного файла"""
        try:
            if os.path.exists(self.data_file):
                backup_name = f"{self.data_file}.backup"
                import shutil
                shutil.copy2(self.data_file, backup_name)
                print(f"Создана резервная копия: {backup_name}")
        except Exception as e:
            print(f"Не удалось создать резервную копию: {e}")
    
    def get_employee_by_name(self, name):
        """
        Найти сотрудника по имени
        
        Args:
            name: имя сотрудника
            
        Returns:
            dict or None: данные сотрудника или None если не найден
        """
        employees = self.load_employees()
        for emp in employees:
            if emp.get('name') == name:
                return emp
        return None
    
    def update_employee(self, name, updates):
        """
        Обновить данные сотрудника
        
        Args:
            name: имя сотрудника
            updates: словарь с обновляемыми полями
            
        Returns:
            bool: True если успешно, False если сотрудник не найден
        """
        employees = self.load_employees()
        
        for emp in employees:
            if emp.get('name') == name:
                emp.update(updates)
                self.save_employees(employees)
                return True
        
        return False
    
    def delete_employee(self, name):
        """
        Удалить сотрудника
        
        Args:
            name: имя сотрудника
            
        Returns:
            bool: True если успешно, False если сотрудник не найден
        """
        employees = self.load_employees()
        
        for i, emp in enumerate(employees):
            if emp.get('name') == name:
                del employees[i]
                self.save_employees(employees)
                return True
        
        return False
    
    def get_month_data(self, employee_name, year, month):
        """
        Получить данные за конкретный месяц
        
        Args:
            employee_name: имя сотрудника
            year: год
            month: месяц (1-12)
            
        Returns:
            dict or None: данные за месяц или None
        """
        employee = self.get_employee_by_name(employee_name)
        if not employee:
            return None
        
        month_key = f"{year}-{month:02d}"
        return employee.get('months', {}).get(month_key)
    
    def export_to_json(self, filepath):
        """
        Экспортировать данные в указанный JSON файл
        
        Args:
            filepath: путь для экспорта
        """
        employees = self.load_employees()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(employees, f, ensure_ascii=False, indent=2)
    
    def import_from_json(self, filepath):
        """
        Импортировать данные из JSON файла
        
        Args:
            filepath: путь к файлу для импорта
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            employees = json.load(f)
        
        # Проверяем структуру
        for emp in employees:
            self._ensure_employee_structure(emp)
        
        self.save_employees(employees)

    def reorder_employees_alphabetically(self):
        """
        Пересортировать сотрудников в файле по алфавиту
        """
        employees = self.load_employees()
        sorted_employees = sorted(
            employees,
            key=lambda e: self._get_sort_key(e.get('name', ''))
        )
        self.save_employees(sorted_employees)
        return sorted_employees