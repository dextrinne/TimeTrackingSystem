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
from pathlib import Path

# ----------------------------------------------------------------------------------------------------------

# Главный контроллер приложения
class TimeTableApp(QObject):
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
        self.update_archive_list()
    
    # Настройка соединений сигналов
    def setup_connections(self):
        self.main_window.month_changed.connect(self.change_month)
        self.main_window.employee_added.connect(self.add_employee)
        self.main_window.employee_edited.connect(self.edit_employee)
        self.main_window.employee_deleted.connect(self.delete_employee)
        self.main_window.day_type_changed.connect(self.change_day_type)
        self.data_changed.connect(self.update_ui)
    
    # Загрузка списка сотрудников
    def load_employees(self):
        self.current_employees = self.data_manager.load_employees()
        # Сортировка по фамилии
        self.sort_employees()
    
    # Сортировка сотрудников по фамилии
    def sort_employees(self):
        self.current_employees.sort(
            key=lambda e: e.get('name', '').split()[0] if e.get('name', '') else ''
        )
    
    # Автоматическое заполнение выходных дней (суббота и воскресенье)
    def auto_fill_weekends(self):
        import calendar
        
        # Получаем количество дней в текущем месяце
        _, days_in_month = calendar.monthrange(self.current_year, self.current_month)
        
        # Для каждого сотрудника
        for emp_idx in range(len(self.current_employees)):
            # Для каждого дня месяца
            for day in range(1, days_in_month + 1):
                # Определяем день недели (0 = понедельник, 6 = воскресенье)
                weekday = calendar.weekday(self.current_year, self.current_month, day)
                
                # Если это суббота (5) или воскресенье (6)
                if weekday in (5, 6):
                    day_key = (emp_idx, day)
                    
                    # Если день еще не заполнен (или пустой)
                    if day_key not in self.day_data:
                        self.day_data[day_key] = {
                            'code': DayTypes.WEEKEND,
                            'hours': 0
                        }
                    elif isinstance(self.day_data[day_key], str):
                        if self.day_data[day_key] == DayTypes.EMPTY:
                            self.day_data[day_key] = {
                                'code': DayTypes.WEEKEND,
                                'hours': 0
                            }
                    elif self.day_data[day_key].get('code') == DayTypes.EMPTY:
                        self.day_data[day_key] = {
                            'code': DayTypes.WEEKEND,
                            'hours': 0
                        }
        
        # Сохраняем изменения
        self.save_month_data()
        
        # Обновляем UI
        self.update_ui()

    # Загрузка данных за текущий месяц
    def load_month_data(self):
        month_key = self.get_month_key()
        
        self.day_data = {}
        month_has_data = False
        
        for emp_idx, employee in enumerate(self.current_employees):
            month_data = employee.get('months', {}).get(month_key, {})
            days_data = month_data.get('days', {})
            
            if days_data:
                month_has_data = True
            
            for day_str, cell_data in days_data.items():
                day = int(day_str)
                # Поддержка старого формата (только код)
                if isinstance(cell_data, str):
                    self.day_data[(emp_idx, day)] = {
                        'code': cell_data,
                        'hours': 0
                    }
                else:
                    self.day_data[(emp_idx, day)] = cell_data
        
        # Если месяц пустой - автоматически заполняем выходные
        if not month_has_data:
            self.auto_fill_weekends()
    
    # Получить ключ месяца
    def get_month_key(self):
        return f"{self.current_year}_{self.current_month:02d}"
    
    # Изменение месяца/года
    def change_month(self, month, year):
        # Сохраняем текущие данные
        self.save_month_data()
        
        # Обновляем текущие параметры
        self.current_month = month
        self.current_year = year
        
        # Загружаем данные за новый месяц
        self.load_month_data()
        
        # Обновляем UI
        self.update_ui()
    
    # Сохранение данных текущего месяца
    def save_month_data(self):
        month_key = self.get_month_key()
        
        employee_days = {}
        for (emp_idx, day), cell_data in self.day_data.items():
            if emp_idx not in employee_days:
                employee_days[emp_idx] = {}
            employee_days[emp_idx][str(day)] = cell_data
        
        for emp_idx, days in employee_days.items():
            if emp_idx < len(self.current_employees):
                if 'months' not in self.current_employees[emp_idx]:
                    self.current_employees[emp_idx]['months'] = {}
                
                if month_key not in self.current_employees[emp_idx]['months']:
                    self.current_employees[emp_idx]['months'][month_key] = {}
                
                self.current_employees[emp_idx]['months'][month_key]['days'] = days
                self.update_employee_statistics(emp_idx, month_key)
        
        self.data_manager.save_employees(self.current_employees)
    
    # Обновление статистики сотрудника за месяц
    def update_employee_statistics(self, emp_idx, month_key):
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
            'other': 0,
            'total_hours': 0  # Добавляем счетчик часов
        }
        
        for day_str, cell_data in days_data.items():
            code = cell_data if isinstance(cell_data, str) else cell_data.get('code', DayTypes.EMPTY)
            hours = 0 if isinstance(cell_data, str) else cell_data.get('hours', 0)
            
            if code == DayTypes.WORKDAY:
                stats['working_days'] += 1
                stats['total_hours'] += hours
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
    
    
    # Добавление сотрудника
    def add_employee(self, employee_data):
        # Добавляем в undo стек
        self.add_to_undo_stack(('add_employee', len(self.current_employees), employee_data))
        
        self.current_employees.append(employee_data)
        self.sort_employees()
        
        # Автоматически заполняем выходные дни для нового сотрудника
        self.auto_fill_weekends_for_employee(len(self.current_employees) - 1)
        
        self.data_manager.save_employees(self.current_employees)
        self.data_changed.emit()
    
    # Автоматическое заполнение выходных дней для конкретного сотрудника
    def auto_fill_weekends_for_employee(self, emp_idx):
        import calendar
        
        _, days_in_month = calendar.monthrange(self.current_year, self.current_month)
        
        for day in range(1, days_in_month + 1):
            weekday = calendar.weekday(self.current_year, self.current_month, day)
            
            # Если это суббота (5) или воскресенье (6)
            if weekday in (5, 6):
                day_key = (emp_idx, day)
                
                # Проверяем, не заполнен ли уже день
                if day_key not in self.day_data:
                    self.day_data[day_key] = {
                        'code': DayTypes.WEEKEND,
                        'hours': 0
                    }
                elif isinstance(self.day_data[day_key], str):
                    if self.day_data[day_key] == DayTypes.EMPTY:
                        self.day_data[day_key] = {
                            'code': DayTypes.WEEKEND,
                            'hours': 0
                        }
                elif self.day_data[day_key].get('code') == DayTypes.EMPTY:
                    self.day_data[day_key] = {
                        'code': DayTypes.WEEKEND,
                        'hours': 0
                    }
        
        # Сохраняем данные месяца
        self.save_month_data()

    # Редактирование сотрудника
    def edit_employee(self, index, employee_data):
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
    
    # Удаление сотрудника
    def delete_employee(self, index):
        if index < len(self.current_employees):
            # Добавляем в undo стек
            deleted_employee = self.current_employees[index].copy()
            self.add_to_undo_stack(('delete_employee', index, deleted_employee))
            
            del self.current_employees[index]
            self.data_manager.save_employees(self.current_employees)
            self.data_changed.emit()
    
    # Изменение типа дня
    def change_day_type(self, day_key, data):
        emp_idx, day = day_key
    
        # Добавляем в undo стек
        old_data = self.day_data.get(day_key, {'code': DayTypes.EMPTY, 'hours': 0})
        self.add_to_undo_stack(('change_day', day_key, old_data))
        
        # Если пришла строка (для обратной совместимости), преобразуем в словарь
        if isinstance(data, str):
            data = {'code': data, 'hours': 0}
        
        if 'code' not in data:
            data['code'] = DayTypes.EMPTY
        if 'hours' not in data:
            data['hours'] = 0
        
        if not data['code'] or not data['code'].strip():
            data['code'] = DayTypes.EMPTY
        
        # Обновляем данные
        self.day_data[day_key] = data
        
        # Обновляем UI
        self.main_window.update_day_cell(emp_idx, day, data)
        
        # Автосохранение
        self.save_month_data()
        
        # Обновляем статистику в таблице сотрудников
        self.update_employees_statistics_ui()
    
    # Обновление статистики в UI
    def update_employees_statistics_ui(self):
        self.main_window.update_employees_table(self.current_employees)
    
    # Добавление действия в стек отмены
    def add_to_undo_stack(self, action):
        self.undo_stack.append(action)
        if len(self.undo_stack) > AppConfig.MAX_UNDO_DEPTH:
            self.undo_stack.pop(0)
    
    # Отмена последнего действия
    def undo_last_action(self):
        if not self.undo_stack:
            return
        
        action = self.undo_stack.pop()
        action_type = action[0]
        
        if action_type == 'change_day':
            day_key, old_data = action[1], action[2]
            self.day_data[day_key] = old_data
            emp_idx, day = day_key
            self.main_window.update_day_cell(emp_idx, day, old_data)
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

    # Обновление пользовательского интерфейса
    def update_ui(self):
        self.main_window.update_calendar(
            self.current_year,
            self.current_month,
            self.current_employees,
            self.day_data
        )
        self.main_window.update_employees_table(self.current_employees)
    
    # Автосохранение данных
    def autosave(self):
        self.save_month_data()
        self.main_window.status_label.setText("Автосохранение выполнено")
    
    # Сохранение всех данных
    def save_data(self):
        self.save_month_data()
        self.data_manager.save_employees(self.current_employees)

    # Сохранение текущего табеля в архив
    def save_current_to_archive(self):
        # Сначала сохраняем текущие данные месяца
        self.save_month_data()
        
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
        
        # Обновляем список архива
        self.update_archive_list()
        
        QMessageBox.information(
            self.main_window,
            "Сохранено",
            f"Табель сохранен в архив:\n{filename}"
        )
    
    # Загрузка выбранного табеля из архива
    def load_selected_from_archive(self):
        selected_items = self.main_window.archive_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self.main_window,
                "Предупреждение",
                "Выберите табель для загрузки"
            )
            return
        
        selected_item = selected_items[0]
        filename = selected_item.text(3)  # Имя файла в 4-й колонке
        
        try:
            filepath = AppConfig.ARCHIVE_DIR / filename
            with open(filepath, 'r', encoding='utf-8') as f:
                archive_data = json.load(f)
            
            # Создаем диалог подтверждения
            msg_box = QMessageBox(self.main_window)
            msg_box.setWindowTitle("Подтверждение")
            msg_box.setText(f"Загрузить табель за {archive_data['month_name']} {archive_data['year']}?\n"
                        "Текущие несохраненные изменения будут потеряны.")
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            # Устанавливаем русский текст на кнопках
            msg_box.button(QMessageBox.StandardButton.Yes).setText("Да")
            msg_box.button(QMessageBox.StandardButton.No).setText("Нет")
            
            # Показываем диалог и получаем результат
            reply = msg_box.exec()

            if reply == QMessageBox.StandardButton.Yes:
                # Сохраняем текущие данные перед загрузкой
                self.save_month_data()
                
                # Загружаем данные из архива
                self.current_year = archive_data['year']
                self.current_month = archive_data['month']
                self.current_employees = archive_data['employees']
                
                # Восстанавливаем day_data
                self.day_data = {}
                for key_str, code in archive_data['day_data'].items():
                    emp_idx_str, day_str = key_str.split('_')
                    self.day_data[(int(emp_idx_str), int(day_str))] = code
                
                # Обновляем UI
                self.update_ui()
                
                # Обновляем архивное дерево
                self.update_archive_list()
                
                QMessageBox.information(
                    self.main_window,
                    "Загружено",
                    f"Табель за {archive_data['month_name']} {archive_data['year']} успешно загружен"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Ошибка загрузки",
                f"Не удалось загрузить табель:\n{str(e)}"
            )
    
    # Удаление выбранного табеля из архива
    def delete_selected_from_archive(self):
        selected_items = self.main_window.archive_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self.main_window,
                "Предупреждение",
                "Выберите табель для удаления"
            )
            return
        
        selected_item = selected_items[0]
        filename = selected_item.text(3)
        month_name = selected_item.text(0)
        year = selected_item.text(1)
        
        # Создаем диалог подтверждения
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText(f"Вы действительно хотите удалить табель за {month_name} {year}?\n"
                        "Это действие нельзя отменить.")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        # Устанавливаем русский текст на кнопках
        msg_box.button(QMessageBox.StandardButton.Yes).setText("Да")
        msg_box.button(QMessageBox.StandardButton.No).setText("Нет")
        
        # Показываем диалог и получаем результат
        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            try:
                filepath = AppConfig.ARCHIVE_DIR / filename
                if filepath.exists():
                    filepath.unlink()  # Удаляем файл
                    
                    # Обновляем список архива
                    self.update_archive_list()
                    
                    QMessageBox.information(
                        self.main_window,
                        "Удалено",
                        f"Табель за {month_name} {year} удален из архива"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self.main_window,
                    "Ошибка удаления",
                    f"Не удалось удалить табель:\n{str(e)}"
                )
    
    # Обновление списка архивных табелей
    def update_archive_list(self):
        archives = []
        archive_dir = AppConfig.ARCHIVE_DIR
        
        if archive_dir.exists():
            for filepath in sorted(archive_dir.glob("timetable_*.json"), reverse=True):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    archives.append({
                        'filename': filepath.name,
                        'month_name': data.get('month_name', 'Неизвестно'),
                        'year': data.get('year', 0),
                        'month': data.get('month', 1),
                        'timestamp': data.get('timestamp', 'Неизвестно')
                    })
                except (json.JSONDecodeError, KeyError):
                    continue
        
        self.main_window.update_archive_tree(archives)
    
# ----------------------------------------------------------------------------------------------------------

    # Экспорт в Excel с выбором папки
    def export_to_excel(self, with_stats=True, with_colors=True):
        try:
            filename = self.template_exporter.export_timetable(
                self.current_year,
                self.current_month,
                self.current_employees,
                self.day_data,
                with_stats,
                with_colors
            )
            
            if filename:
                QMessageBox.information(
                    self.main_window,
                    "Экспорт завершен",
                    f"Табель успешно экспортирован в файл:\n{filename}"
                )
                self.main_window.status_label.setText(f"Табель экспортирован: {Path(filename).name}")
            else:
                self.main_window.status_label.setText("Экспорт отменен")
                
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Ошибка экспорта",
                f"Не удалось экспортировать табель:\n{str(e)}"
            )
            self.main_window.status_label.setText("Ошибка экспорта")

    # Экспорт в Excel с указанным путем
    def export_to_excel_with_path(self, save_path, with_stats=True, with_colors=True):
        try:
            filename = self.template_exporter.export_timetable(
                self.current_year,
                self.current_month,
                self.current_employees,
                self.day_data,
                with_stats,
                with_colors,
                save_path
            )
            
            if filename:
                QMessageBox.information(
                    self.main_window,
                    "Экспорт завершен",
                    f"Табель успешно экспортирован в файл:\n{filename}"
                )
                self.main_window.status_label.setText(f"Экспортировано: {Path(filename).name}")
            else:
                self.main_window.status_label.setText("Экспорт отменен")
                
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Ошибка экспорта",
                f"Не удалось экспортировать табель:\n{str(e)}"
            )
            self.main_window.status_label.setText("Ошибка экспорта")
    
    def run(self):
        """Запуск приложения"""
        self.main_window.show()

# ----------------------------------------------------------------------------------------------------------

# Точка входа в приложение
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Современный стиль
    
    # Создание необходимых директорий
    AppConfig.ensure_directories()
    
    # Создание и запуск приложения
    time_table_app = TimeTableApp()
    time_table_app.run()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()