from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
import sys
import os
from datetime import datetime
import json
import calendar

from frontend.config import AppConfig
from frontend.styles import DayTypes
from ui.main_window import MainWindow
from core.data_manager import DataManager
from core.template_exporter import TemplateExporter


class TimeTableApp(QObject):
    """Главный контроллер приложения"""
    
    data_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.template_exporter = TemplateExporter()
        
        # Текущее состояние
        self.current_year = AppConfig.DEFAULT_YEAR
        self.current_month = AppConfig.DEFAULT_MONTH
        self.current_employees = []
        self.day_data = {}
        self.undo_stack = []
        
        # Инициализация
        self.load_employees()
        self.load_month_data()
        
        # Создание главного окна
        self.main_window = MainWindow(self)
        
        # Настройка автосохранения
        if AppConfig.AUTOSAVE_ENABLED:
            self.autosave_timer = QTimer()
            self.autosave_timer.timeout.connect(self.autosave)
            self.autosave_timer.start(AppConfig.AUTOSAVE_DELAY)
        
        # Подключение сигналов
        self.setup_connections()
        
        # Первоначальное обновление UI
        self.update_ui()
    
    def setup_connections(self):
        """Настройка соединений сигналов"""
        self.main_window.month_changed.connect(self.change_month)
        self.main_window.employee_added.connect(self.add_employee)
        self.main_window.employee_edited.connect(self.edit_employee)
        self.main_window.employee_deleted.connect(self.delete_employee)
        self.main_window.day_type_changed.connect(self.change_day_type)
        self.data_changed.connect(self.update_ui)
    
    def load_employees(self):
        """Загрузка списка сотрудников"""
        self.current_employees = self.data_manager.load_employees()
        # Сортировка по фамилии
        self.sort_employees()
    
    def sort_employees(self):
        """Сортировка сотрудников по фамилии"""
        self.current_employees.sort(
            key=lambda e: e.get('name', '').split()[0] if e.get('name', '') else ''
        )
    
    def load_month_data(self):
        """Загрузка данных за текущий месяц"""
        month_key = self.get_month_key()
        
        self.day_data = {}
        for emp_idx, employee in enumerate(self.current_employees):
            month_data = employee.get('months', {}).get(month_key, {})
            days_data = month_data.get('days', {})
            
            for day_str, code in days_data.items():
                day = int(day_str)
                self.day_data[(emp_idx, day)] = code
    
    def get_month_key(self):
        """Получить ключ месяца"""
        return f"{self.current_year}_{self.current_month:02d}"
    
    def change_month(self, month, year):
        """Изменение месяца/года"""
        # Сохраняем текущие данные
        self.save_month_data()
        
        # Обновляем текущие параметры
        self.current_month = month
        self.current_year = year
        
        # Загружаем данные за новый месяц
        self.load_month_data()
        
        # Обновляем UI
        self.update_ui()
    
    def save_month_data(self):
        """Сохранение данных текущего месяца"""
        month_key = self.get_month_key()
        
        # Группируем данные по сотрудникам
        employee_days = {}
        for (emp_idx, day), code in self.day_data.items():
            if emp_idx not in employee_days:
                employee_days[emp_idx] = {}
            employee_days[emp_idx][str(day)] = code
        
        # Обновляем данные сотрудников
        for emp_idx, days in employee_days.items():
            if emp_idx < len(self.current_employees):
                if 'months' not in self.current_employees[emp_idx]:
                    self.current_employees[emp_idx]['months'] = {}
                
                if month_key not in self.current_employees[emp_idx]['months']:
                    self.current_employees[emp_idx]['months'][month_key] = {}
                
                self.current_employees[emp_idx]['months'][month_key]['days'] = days
                
                # Обновляем статистику
                self.update_employee_statistics(emp_idx, month_key)
        
        # Сохраняем в файл
        self.data_manager.save_employees(self.current_employees)
    
    def update_employee_statistics(self, emp_idx, month_key):
        """Обновление статистики сотрудника за месяц"""
        if emp_idx >= len(self.current_employees):
            return
        
        employee = self.current_employees[emp_idx]
        month_data = employee.get('months', {}).get(month_key, {})
        days_data = month_data.get('days', {})
        
        stats = {
            'working_days': 0,
            'weekends': 0,
            'vacation': 0,
            'sick_leave': 0,
            'other': 0
        }
        
        for day_str, code in days_data.items():
            if code == DayTypes.WORKDAY:
                stats['working_days'] += 1
            elif code == DayTypes.WEEKEND:
                stats['weekends'] += 1
            elif code in [DayTypes.VACATION_MAIN, DayTypes.VACATION_EXTRA]:
                stats['vacation'] += 1
            elif code == DayTypes.SICK:
                stats['sick_leave'] += 1
            elif code != DayTypes.EMPTY:
                stats['other'] += 1
        
        month_data.update(stats)
        employee['months'][month_key] = month_data
    
    def add_employee(self, employee_data):
        """Добавление сотрудника"""
        # Добавляем в undo стек
        self.add_to_undo_stack(('add_employee', len(self.current_employees), employee_data))
        
        self.current_employees.append(employee_data)
        self.sort_employees()
        self.data_manager.save_employees(self.current_employees)
        self.data_changed.emit()
    
    def edit_employee(self, index, employee_data):
        """Редактирование сотрудника"""
        if index < len(self.current_employees):
            # Добавляем в undo стек
            old_data = self.current_employees[index].copy()
            self.add_to_undo_stack(('edit_employee', index, old_data))
            
            # Сохраняем существующие данные месяцев
            if 'months' in self.current_employees[index]:
                employee_data['months'] = self.current_employees[index]['months']
            
            self.current_employees[index] = employee_data
            self.sort_employees()
            self.data_manager.save_employees(self.current_employees)
            self.data_changed.emit()
    
    def delete_employee(self, index):
        """Удаление сотрудника"""
        if index < len(self.current_employees):
            # Добавляем в undo стек
            deleted_employee = self.current_employees[index].copy()
            self.add_to_undo_stack(('delete_employee', index, deleted_employee))
            
            del self.current_employees[index]
            self.data_manager.save_employees(self.current_employees)
            self.data_changed.emit()
    
    def change_day_type(self, day_key, code):
        """Изменение типа дня"""
        emp_idx, day = day_key
        
        # Добавляем в undo стек
        old_code = self.day_data.get(day_key, DayTypes.EMPTY)
        self.add_to_undo_stack(('change_day', day_key, old_code))
        
        # Обновляем данные
        if code == DayTypes.EMPTY:
            if day_key in self.day_data:
                del self.day_data[day_key]
        else:
            self.day_data[day_key] = code
        
        # Обновляем UI
        self.main_window.update_day_cell(emp_idx, day, code)
        
        # Автосохранение
        self.save_month_data()
        
        # Обновляем статистику в таблице сотрудников
        self.update_employees_statistics_ui()
    
    def update_employees_statistics_ui(self):
        """Обновление статистики в UI"""
        self.main_window.update_employees_table(self.current_employees)
    
    def add_to_undo_stack(self, action):
        """Добавление действия в стек отмены"""
        self.undo_stack.append(action)
        if len(self.undo_stack) > AppConfig.MAX_UNDO_DEPTH:
            self.undo_stack.pop(0)
    
    def undo_last_action(self):
        """Отмена последнего действия"""
        if not self.undo_stack:
            return
        
        action = self.undo_stack.pop()
        action_type = action[0]
        
        if action_type == 'change_day':
            day_key, old_code = action[1], action[2]
            self.day_data[day_key] = old_code
            emp_idx, day = day_key
            self.main_window.update_day_cell(emp_idx, day, old_code)
            self.save_month_data()
            self.update_employees_statistics_ui()
            
        elif action_type == 'add_employee':
            index = action[1]
            if index < len(self.current_employees):
                del self.current_employees[index]
                self.data_manager.save_employees(self.current_employees)
                self.data_changed.emit()
                
        elif action_type == 'edit_employee':
            index, old_data = action[1], action[2]
            if index < len(self.current_employees):
                self.current_employees[index] = old_data
                self.data_manager.save_employees(self.current_employees)
                self.data_changed.emit()
                
        elif action_type == 'delete_employee':
            index, employee_data = action[1], action[2]
            self.current_employees.insert(index, employee_data)
            self.data_manager.save_employees(self.current_employees)
            self.data_changed.emit()
    
    def update_ui(self):
        """Обновление пользовательского интерфейса"""
        self.main_window.update_calendar(
            self.current_year,
            self.current_month,
            self.current_employees,
            self.day_data
        )
        self.main_window.update_employees_table(self.current_employees)
    
    def autosave(self):
        """Автосохранение данных"""
        self.save_month_data()
        self.main_window.status_label.setText("Автосохранение выполнено")
    
    def save_data(self):
        """Сохранение всех данных"""
        self.save_month_data()
        self.data_manager.save_employees(self.current_employees)
    
    def export_to_excel(self, with_stats=True, with_colors=True):
        """Экспорт в Excel"""
        try:
            filename = self.template_exporter.export_timetable(
                self.current_year,
                self.current_month,
                self.current_employees,
                self.day_data,
                with_stats,
                with_colors
            )
            QMessageBox.information(
                self.main_window,
                "Экспорт завершен",
                f"Табель успешно экспортирован в файл:\n{filename}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Ошибка экспорта",
                f"Не удалось экспортировать табель:\n{str(e)}"
            )
    
    def save_current_to_archive(self):
        """Сохранение текущего табеля в архив"""
        archive_data = {
            'year': self.current_year,
            'month': self.current_month,
            'month_name': AppConfig.MONTHS[self.current_month - 1],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'employees': self.current_employees,
            'day_data': {f"{k[0]}_{k[1]}": v for k, v in self.day_data.items()}
        }
        
        filename = f"timetable_{self.current_year}_{self.current_month:02d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = AppConfig.ARCHIVE_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=2)
        
        QMessageBox.information(
            self.main_window,
            "Сохранено",
            f"Табель сохранен в архив:\n{filename}"
        )
    
    def load_selected_from_archive(self):
        """Загрузка выбранного табеля из архива"""
        # Реализация загрузки из архива
        pass
    
    def delete_selected_from_archive(self):
        """Удаление выбранного табеля из архива"""
        # Реализация удаления из архива
        pass
    
    def run(self):
        """Запуск приложения"""
        self.main_window.show()


def main():
    """Точка входа в приложение"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Современный стиль
    
    # Установка иконки приложения (если есть)
    # app.setWindowIcon(QIcon('path/to/icon.png'))
    
    # Создание необходимых директорий
    AppConfig.ensure_directories()
    
    # Создание и запуск приложения
    time_table_app = TimeTableApp()
    time_table_app.run()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()