import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import calendar
import json
import os

from core.data_manager import DataManager
from core.template_exporter import TemplateExporter
from ui.main_window import MainWindow
from frontend.styles import DayTypes, Colors, Fonts
from frontend.config import AppConfig


class TimeTableApp:
    """Главное приложение с табелем в календарном формате"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(AppConfig.APP_TITLE)
        self.root.geometry(AppConfig.WINDOW_SIZE)
        self.root.resizable(True, True)
        
        # Создаем необходимые директории
        AppConfig.ensure_directories()
        
        # Инициализация менеджеров
        self.data_manager = DataManager(str(AppConfig.EMPLOYEES_FILE))
        self.exporter = TemplateExporter()
        
        # Текущие данные
        self.current_employees = []
        self.current_month = AppConfig.DEFAULT_MONTH
        self.current_year = AppConfig.DEFAULT_YEAR
        self.day_buttons = {}
        self.day_data = {}
        
        # История для Ctrl+Z
        self.undo_stack = []
        self.max_undo_depth = AppConfig.MAX_UNDO_DEPTH
        
        # Флаг для отложенного сохранения
        self.save_pending = False
        self.save_timer = None
        
        # Получить количество дней в месяце
        self.days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        
        # Загружаем данные
        self.load_employees()
        self.load_day_data()
        
        # Создаем UI
        self.ui = MainWindow(root, self)
        
        # Привязка клавиш
        self.root.bind("<Control-z>", lambda e: self.on_undo())
        self.root.bind("<MouseWheel>", self.ui.on_mousewheel)
        self.root.bind("<Button-4>", self.ui.on_mousewheel)
        self.root.bind("<Button-5>", self.ui.on_mousewheel)
    
    def get_month_key(self):
        """Получить ключ месяца-года для сохранения (YYYY-MM)"""
        return f"{self.current_year}-{self.current_month:02d}"
    
    def load_employees(self):
        """Загрузка сотрудников с сортировкой по алфавиту"""
        employees = self.data_manager.load_employees()
        
        # Сортировка по фамилии (первое слово в ФИО)
        self.current_employees = sorted(
            employees, 
            key=lambda e: self._get_sort_key(e.get('name', ''))
        )

    def _get_sort_key(self, full_name):
        """
        Получить ключ для сортировки по фамилии
        
        Args:
            full_name: полное ФИО сотрудника
        
        Returns:
            str: ключ для сортировки (фамилия в нижнем регистре)
        """
        if not full_name:
            return ''
        
        # Разбиваем ФИО на части
        parts = full_name.split()
        
        # Если есть хотя бы одна часть, используем её как фамилию
        if parts:
            return parts[0].lower()
        
        return full_name.lower()
    
    def load_day_data(self):
        """Загрузка данных дней для текущего месяца"""
        self.day_data = {}
        self.days_in_month = calendar.monthrange(self.current_year, self.current_month)[1]
        month_key = self.get_month_key()
        
        # Маппинг старых кодов на новые (для обратной совместимости)
        code_mapping = {
            'Р': DayTypes.WORKDAY,
            'В': DayTypes.WEEKEND,
            'О': DayTypes.VACATION_MAIN,  # Старый код отпуска
            'Б': DayTypes.SICK,
            'П': DayTypes.UNPAID,  # Старый код "прочее" маппим на неоплачиваемый отпуск
        }
        
        try:
            employees = self.data_manager.load_employees()
            for emp_idx, employee in enumerate(employees):
                day_string = ''
                has_real_data = False
                
                if 'months' in employee and month_key in employee['months']:
                    day_string = employee['months'][month_key].get('day_data', '')
                elif 'day_data' in employee and employee['day_data']:
                    day_string = employee['day_data']
                
                if day_string:
                    cleaned = day_string.replace(' ', '').replace('|', '')
                    has_real_data = len(cleaned) > 0
                
                if has_real_data and day_string:
                    weeks = day_string.split('|')
                    day_counter = 0
                    for week in weeks:
                        for code in week:
                            day_counter += 1
                            if day_counter <= self.days_in_month:
                                key = (emp_idx, day_counter)
                                
                                # Конвертируем старые коды в новые
                                if code in code_mapping:
                                    code = code_mapping[code]
                                
                                if code in DayTypes.TYPES:
                                    self.day_data[key] = code
                else:
                    # Автозаполнение для новых/пустых месяцев
                    for day in range(1, self.days_in_month + 1):
                        date_obj = datetime(self.current_year, self.current_month, day)
                        weekday = date_obj.weekday()
                        
                        if weekday >= 5:
                            day_code = DayTypes.WEEKEND
                        else:
                            day_code = DayTypes.WORKDAY
                        
                        key = (emp_idx, day)
                        self.day_data[key] = day_code
        except Exception as e:
            print(f"Ошибка при загрузке дней: {e}")
    
    def save_day_data(self):
        """Сохранение данных дней в сотрудников"""
        month_key = self.get_month_key()
        employees = self.data_manager.load_employees()
        
        for emp_idx, employee in enumerate(employees):
            if 'months' not in employee:
                employee['months'] = {}
            
            if month_key not in employee['months']:
                employee['months'][month_key] = {
                    'working_days': 0,
                    'weekends': 0,
                    'vacation': 0,
                    'sick_leave': 0,
                    'other': 0,
                    'day_data': ''
                }
            
            day_string = ""
            for day in range(1, self.days_in_month + 1):
                key = (emp_idx, day)
                code = self.day_data.get(key, DayTypes.EMPTY)
                day_string += code
                
                if day % 7 == 0:
                    day_string += "|"
            
            if not day_string.endswith("|"):
                day_string += "|"
            
            employee['months'][month_key]['day_data'] = day_string
            
            # Подсчет статистики по всем типам дней
            counts = {}
            for day in range(1, self.days_in_month + 1):
                key = (emp_idx, day)
                code = self.day_data.get(key, DayTypes.EMPTY)
                counts[code] = counts.get(code, 0) + 1
            
            # Группировка статистики для совместимости со старым форматом
            employee['months'][month_key]['working_days'] = (
                counts.get(DayTypes.WORKDAY, 0) + 
                counts.get(DayTypes.NIGHT, 0) + 
                counts.get(DayTypes.WEEKEND_WORK, 0) + 
                counts.get(DayTypes.OVERTIME, 0)
            )
            
            employee['months'][month_key]['weekends'] = (
                counts.get(DayTypes.WEEKEND, 0) + 
                counts.get(DayTypes.NONWORK_PAID, 0)
            )
            
            employee['months'][month_key]['vacation'] = (
                counts.get(DayTypes.VACATION_MAIN, 0) + 
                counts.get(DayTypes.VACATION_EXTRA, 0) + 
                counts.get(DayTypes.STUDY, 0) + 
                counts.get(DayTypes.UNPAID, 0) + 
                counts.get(DayTypes.CHILD_CARE, 0)
            )
            
            employee['months'][month_key]['sick_leave'] = counts.get(DayTypes.SICK, 0)
            
            employee['months'][month_key]['other'] = (
                counts.get(DayTypes.ABSENTEEISM, 0) + 
                counts.get(DayTypes.BUSINESS_TRIP, 0) + 
                counts.get(DayTypes.UNKNOWN, 0) + 
                counts.get(DayTypes.ADMIN_PERMIT, 0) + 
                counts.get(DayTypes.STATE_DUTY, 0) + 
                counts.get(DayTypes.TRANSITION, 0)
            )
        
        self.data_manager.save_employees(employees)
        self.current_employees = employees
    
    def set_day_type(self, day_key, code):
        """Установить тип дня"""
        emp_idx, day = day_key
        if emp_idx >= len(self.current_employees) or day > self.days_in_month:
            return
        
        self.push_undo_snapshot()
        self.day_data[day_key] = code
        
        if day_key in self.day_buttons:
            name, color, _ = DayTypes.TYPES[code]
            btn = self.day_buttons[day_key]
            btn.config(bg=color, text=code if code != DayTypes.EMPTY else '')
        
        self.schedule_autosave()
    
    def on_day_click(self, day_key):
        """Клик на день - переключить на следующий тип"""
        emp_idx, day = day_key
        current_code = self.day_data.get(day_key, DayTypes.EMPTY)
        
        current_idx = DayTypes.ORDER.index(current_code)
        next_idx = (current_idx + 1) % len(DayTypes.ORDER)
        next_code = DayTypes.ORDER[next_idx]
        
        if next_code != current_code:
            self.set_day_type(day_key, next_code)
    
    def on_day_right_click(self, day_key):
        """Правый клик на день - показать меню выбора со всеми типами"""
        menu = tk.Menu(self.root, tearoff=0)
        
        # Создаем подменю по группам
        for group_name, type_codes in DayTypes.TYPE_GROUPS.items():
            submenu = tk.Menu(menu, tearoff=0)
            
            for code in type_codes:
                name, color, short = DayTypes.TYPES[code]
                # Добавляем цветную иконку через emoji или текст
                display_text = f"{code} - {name}"
                submenu.add_command(
                    label=display_text,
                    command=lambda c=code: self.set_day_type(day_key, c)
                )
            
            menu.add_cascade(label=f"{group_name}", menu=submenu)
        
        # Добавляем разделитель и пустой тип
        menu.add_separator()
        menu.add_command(
            label="Очистить",
            command=lambda: self.set_day_type(day_key, DayTypes.EMPTY)
        )
        
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()
    
    def on_month_changed(self, month_name):
        """Смена месяца"""
        months_list = AppConfig.MONTHS
        self.current_month = months_list.index(month_name) + 1
        self.undo_stack = []
        self.load_day_data()
        self.ui.create_timetable()
    
    def on_year_changed(self, year):
        """Смена года"""
        try:
            self.current_year = int(year)
            self.undo_stack = []
            self.load_day_data()
            self.ui.create_timetable()
        except ValueError:
            pass
    
    def push_undo_snapshot(self):
        """Сохранить текущее состояние в стек отмены"""
        snapshot = {
            'day_data': dict(self.day_data),
            'employees': [dict(emp) for emp in self.current_employees]
        }
        self.undo_stack.append(snapshot)
        
        if len(self.undo_stack) > self.max_undo_depth:
            self.undo_stack.pop(0)
    
    def schedule_autosave(self):
        """Запланировать автосохранение"""
        if self.save_timer is not None:
            self.root.after_cancel(self.save_timer)
        
        self.save_timer = self.root.after(AppConfig.AUTOSAVE_DELAY, self.save_day_data)
    
    def on_undo(self):
        """Отмена последнего действия"""
        if not self.undo_stack:
            return
        
        snapshot = self.undo_stack.pop()
        self.day_data = snapshot['day_data']
        self.current_employees = snapshot['employees']
        
        self.ui.create_timetable()
        
        if self.save_timer is not None:
            self.root.after_cancel(self.save_timer)
        self.save_day_data()
    
    def add_employee(self):
        """Добавление сотрудника с последующей сортировкой"""
        from ui.dialogs import EmployeeDialog
        dialog = EmployeeDialog(self.root, "Добавить сотрудника")
        
        if dialog.result:
            new_emp = {
                'name': dialog.result['name'],
                'position': dialog.result['position'],
                'rate': dialog.result['rate'],
                'working_days': 0,
                'weekends': 0,
                'vacation': 0,
                'sick_leave': 0,
                'other': 0,
                'day_data': '',
                'months': {}
            }
            self.current_employees.append(new_emp)
            
            # Сортируем список сотрудников
            self.current_employees = sorted(
                self.current_employees,
                key=lambda e: self._get_sort_key(e.get('name', ''))
            )
            
            self.data_manager.save_employees(self.current_employees)
            
            # Перезагружаем данные дней с учетом нового порядка
            self.load_day_data()
            
            self.ui.refresh_employees_tree()
            self.ui.create_timetable()
            messagebox.showinfo("Успешно", "Сотрудник добавлен!")
    
    def edit_employee_dialog(self):
        """Редактирование сотрудника с сохранением сортировки"""
        selected = self.ui.get_selected_employee()
        if selected is None:
            return
        
        emp_idx, employee = selected
        from ui.dialogs import EmployeeDialog
        dialog = EmployeeDialog(self.root, "Редактировать сотрудника", employee)
        
        if dialog.result:
            self.push_undo_snapshot()
            
            old_name = employee.get('name', '')
            employee['name'] = dialog.result['name']
            employee['position'] = dialog.result['position']
            employee['rate'] = dialog.result['rate']
            
            # Если изменилось имя, пересортировываем список
            if old_name != dialog.result['name']:
                self.current_employees = sorted(
                    self.current_employees,
                    key=lambda e: self._get_sort_key(e.get('name', ''))
                )
            
            self.data_manager.save_employees(self.current_employees)
            
            # Перезагружаем данные дней с учетом возможного изменения порядка
            self.load_day_data()
            
            self.ui.refresh_employees_tree()
            self.ui.create_timetable()
            messagebox.showinfo("Успешно", "Данные сотрудника обновлены!")

    def delete_employee(self):
        """Удаление сотрудника"""
        selected = self.ui.get_selected_employee()
        if selected is None:
            return
        
        emp_idx, employee = selected
        if messagebox.askyesno("Подтверждение", 
                            f"Вы уверены, что хотите удалить сотрудника:\n{employee.get('name', '')}?"):
            del self.current_employees[emp_idx]
            self.day_data = {}
            self.data_manager.save_employees(self.current_employees)
            self.ui.refresh_employees_tree()
            self.load_day_data()
            self.ui.create_timetable()
            messagebox.showinfo("Успешно", "Сотрудник удален!")
    
    def export_to_excel(self):
        """Экспорт в Excel"""
        if not self.current_employees:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xls",
            filetypes=[("Excel files", "*.xls"), ("All files", "*.*")],
            initialfile=f"табель-{AppConfig.MONTHS[self.current_month - 1]}-{self.current_year}.xls"
        )
        
        if file_path:
            try:
                month_name = AppConfig.MONTHS[self.current_month - 1]
                template_path = self._find_template()
                
                if not template_path:
                    template_path = filedialog.askopenfilename(
                        title="Выберите файл шаблона табеля (.xls)",
                        filetypes=[("Excel files", "*.xls"), ("All files", "*.*")]
                    )
                    
                    if not template_path:
                        messagebox.showerror("Ошибка", 
                            "Не найден шаблон табеля.\n\n"
                            "Поместите файл табеля в директорию:\n"
                            f"{os.getcwd()}")
                        return
                
                self.exporter.export_to_excel(
                    self.current_employees,
                    template_path,
                    file_path,
                    month_name,
                    self.current_year
                )
                messagebox.showinfo("Успешно", f"Файл сохранен: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    def _find_template(self):
        """Найти шаблон табеля"""
        month_name = AppConfig.MONTHS[self.current_month - 1]
        
        template_candidates = [
            f'табель-{month_name}{self.current_year}.xls',
            f'табель-{month_name}.xls',
            'табель-январь2026.xls'
        ]
        
        for candidate in template_candidates:
            if os.path.exists(candidate):
                return candidate
        
        for file in os.listdir('.'):
            if file.endswith('.xls') and 'табель' in file.lower():
                return file
        
        return None
    
    def get_archive_dir(self):
        """Получить путь к папке архива"""
        archive_dir = os.path.join(os.path.dirname(__file__), '..', 'archive')
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        return archive_dir
    
    def save_current_to_archive(self):
        """Сохранить текущий табель в архив"""
        try:
            self.save_day_data()
            
            month_name = AppConfig.MONTHS[self.current_month - 1]
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            filename = f"табель_{self.current_year}_{self.current_month:02d}_{month_name}_{timestamp}.json"
            archive_path = os.path.join(self.get_archive_dir(), filename)
            
            archive_data = {
                'year': self.current_year,
                'month': self.current_month,
                'month_name': month_name,
                'timestamp': timestamp,
                'employees': self.current_employees
            }
            
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(archive_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Успешно", f"Табель сохранен в архив:\n{filename}")
            self.ui.refresh_archive_list()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении в архив: {str(e)}")
    
    def load_selected_from_archive(self):
        """Загрузить табель из архива"""
        try:
            filename = self.ui.get_selected_archive()
            if not filename:
                return
            
            filepath = os.path.join(self.get_archive_dir(), filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                archive_data = json.load(f)
            
            self.current_year = archive_data.get('year', AppConfig.DEFAULT_YEAR)
            self.current_month = archive_data.get('month', AppConfig.DEFAULT_MONTH)
            self.current_employees = archive_data.get('employees', [])
            
            self.ui.update_month_year_controls(self.current_month, self.current_year)
            self.undo_stack = []
            
            self.load_day_data()
            self.ui.create_timetable()
            self.ui.refresh_employees_tree()
            
            self.save_day_data()
            
            messagebox.showinfo("Успешно", f"Табель загружен из архива:\n{filename}")
            self.ui.select_timetable_tab()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке архива: {str(e)}")
    
    def delete_selected_from_archive(self):
        """Удалить табель из архива"""
        try:
            filename = self.ui.get_selected_archive()
            if not filename:
                return
            
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот табель из архива?"):
                filepath = os.path.join(self.get_archive_dir(), filename)
                os.remove(filepath)
                messagebox.showinfo("Успешно", "Табель удален из архива")
                self.ui.refresh_archive_list()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении архива: {str(e)}")
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        if self.save_timer is not None:
            self.root.after_cancel(self.save_timer)
        
        self.save_day_data()
        self.root.destroy()