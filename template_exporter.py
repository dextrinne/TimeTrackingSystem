#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Экспортер табелей на основе шаблона (.xls) с использованием xlrd/xlwt
"""

import xlrd
from xlwt import Workbook as XLSWorkbook, easyxf
import calendar
import os


class TemplateExporter:
    """Экспортер табелей на основе .xls шаблона"""
    
    # Карта дней месяца -> колонка в листе стр.2 (0-индексировано)
    DAY_COLUMNS = {
        1: 22, 2: 26, 3: 30, 4: 34, 5: 38, 6: 42, 7: 46, 8: 50,
        9: 54, 10: 58, 11: 62, 12: 66, 13: 70, 14: 74, 15: 78,
        16: 89, 17: 93, 18: 97, 19: 101, 20: 105, 21: 109, 22: 113,
        23: 117, 24: 121, 25: 125, 26: 129, 27: 133, 28: 137, 29: 141,
        30: 145, 31: 149
    }
    
    # Коды дней
    DAY_CODES = {
        'Р': 'ДО',     # Рабочий день (День Обыкновенный)
        'В': 'ДО',     # Выходной (В дни 1-18 тоже кодируется как ДО, в дни 19-31 как В)
        'О': 'ОТ',     # Отпуск (ОТпуск)
        'Б': 'Б',      # Больничный
        'П': 'ПР',     # Прочее (ПРочее)
        ' ': '',       # Пусто
    }
    
    def export_to_excel(self, employees, template_path, output_path, month_name, year):
        """
        Экспорт табеля с использованием шаблона
        
        Args:
            employees: Список сотрудников
            template_path: Путь к файлу шаблона (напр. 'табель-январь2026.xls')
            output_path: Путь для сохранения результата
            month_name: Название месяца (напр. 'январь')
            year: Год
        """
        
        # Загрузим шаблон
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Шаблон не найден: {template_path}")
        
        try:
            # Открываем шаблон для чтения
            template_xlrd = xlrd.open_workbook(template_path)
            
            # Создаем новую рабочую книгу xlwt
            wb = XLSWorkbook()
            
            # Лист 1 - титульная страница (копируем из шаблона как есть)
            self._copy_title_sheet(wb, template_xlrd)
            
            # Лист 2 - данные с сотрудниками
            self._create_data_sheet(wb, employees, template_xlrd, month_name, year)
            
            # Сохраняем результат
            wb.save(output_path)
            
        except Exception as e:
            raise Exception(f"Ошибка при создании табеля: {str(e)}")
    
    def _copy_title_sheet(self, wb, template_xlrd):
        """Копирует титульный лист из шаблона"""
        try:
            sheet_template = template_xlrd.sheet_by_index(0)
            ws = wb.add_sheet("стр.1")
            
            # Создаем один стиль для всех ячеек
            default_style = easyxf('')
            
            # Копируем значения без чрезмерного форматирования
            for r in range(sheet_template.nrows):
                for c in range(sheet_template.ncols):
                    cell_value = sheet_template.cell_value(r, c)
                    # Пишем значение с базовым стилем
                    ws.write(r, c, cell_value, default_style)
                    
        except Exception as e:
            print(f"Ошибка при копировании титульного листа: {e}")
            raise
    
    def _create_data_sheet(self, wb, employees, template_xlrd, month_name, year):
        """Создает лист с данными сотрудников"""
        
        try:
            # Добавляем новый лист
            ws = wb.add_sheet("стр.2")
            
            # Копируем заголовки из шаблона с базовым стилем
            template_sheet = template_xlrd.sheet_by_index(1)
            default_style = easyxf('')
            
            # Копируем первые 3 строки (заголовки и нумерацию)
            for r in range(min(3, template_sheet.nrows)):
                for c in range(template_sheet.ncols):
                    cell_value = template_sheet.cell_value(r, c)
                    ws.write(r, c, cell_value, default_style)
            
            # Получаем количество дней в месяце
            month_num = self._get_month_number(month_name)
            days_in_month = calendar.monthrange(year, month_num)[1]
            
            # Добавляем данные сотрудников (начиная со строки 4, индекс 3)
            current_row = 3
            
            for emp_idx, employee in enumerate(employees):
                # Получаем месячные данные
                month_key = f"{year}-{month_num:02d}"
                month_data = employee.get('months', {}).get(month_key, {})
                day_data_str = month_data.get('day_data', '')
                
                # Парсим day_data (формат: "Р В О | Р В О | ...")
                day_codes = self._parse_day_data(day_data_str, days_in_month)
                
                # ===== ПЕРВАЯ СТРОКА СОТРУДНИКА (коды дней и часы) =====
                ws.write(current_row, 0, emp_idx + 1, default_style)
                ws.write(current_row, 1, employee.get('name', ''), default_style)
                ws.write(current_row, 13, employee.get('position', ''), default_style)
                
                # Заполняем дни месяца в первой строке
                # ВАЖНО: структура зависит от дня месяца!
                # Дни 1-18: пишем только во вторую строку (коды дней)
                # Дни 19-31: пишем в первую строку (часы для рабочих, В для выходных)
                for day in range(1, days_in_month + 1):
                    col = self.DAY_COLUMNS.get(day)
                    if col:
                        code = day_codes.get(day, ' ')
                        
                        if day <= 18:
                            # Дни 1-18: НИЧЕГО не пишем в первую строку
                            pass
                        else:
                            # Дни 19-31: пишем часы/коды выходных в первую строку
                            if code == 'Р':
                                # Рабочий день - часы
                                hours = 8 * employee.get('rate', 1.0)
                                if hours == int(hours):
                                    cell_value = int(hours)
                                else:
                                    cell_value = hours
                                ws.write(current_row, col, cell_value, default_style)
                            elif code == 'В':
                                # Выходной - пишем "В"
                                ws.write(current_row, col, 'В', default_style)
                            elif code in ['О', 'Б', 'П']:
                                # Отпуск, больничный, прочее
                                excel_code = self.DAY_CODES.get(code, '')
                                if excel_code:
                                    ws.write(current_row, col, excel_code, default_style)
                
                # ===== ВТОРАЯ СТРОКА СОТРУДНИКА (ставка и коды дней) =====
                current_row += 1
                ws.write(current_row, 13, employee.get('rate', 1.0), default_style)
                
                # Заполняем коды дней во вторую строку
                # ВАЖНО: структура зависит от дня месяца!
                # Дни 1-18: пишем коды дней (ДО, В, ОТ, Б, ПР)
                # Дни 19-31: НИЧЕГО не пишем (всё уже в первой строке)
                for day in range(1, days_in_month + 1):
                    col = self.DAY_COLUMNS.get(day)
                    if col:
                        code = day_codes.get(day, ' ')
                        excel_code = self.DAY_CODES.get(code, '')
                        
                        if day <= 18:
                            # Дни 1-18: пишем коды дней
                            if excel_code:
                                ws.write(current_row, col, excel_code, default_style)
                        else:
                            # Дни 19-31: НИЧЕГО не пишем
                            pass
                
                current_row += 1
                
        except Exception as e:
            print(f"Ошибка при создании листа данных: {e}")
            raise
    
    def _parse_day_data(self, day_data_str, days_in_month):
        """
        Парсит строку дневных данных в словарь {день: код}
        Формат: "Р В О | Р В О | ..." где | разделяет недели
        """
        day_codes = {}
        
        if not day_data_str:
            return day_codes
        
        weeks = day_data_str.split('|')
        day_counter = 0
        
        for week in weeks:
            for char in week:
                day_counter += 1
                if day_counter <= days_in_month and char in ['Р', 'В', 'О', 'Б', 'П', ' ']:
                    day_codes[day_counter] = char
        
        return day_codes
    
    def _get_month_number(self, month_name):
        """Преобразует название месяца в номер"""
        months = {
            'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4,
            'май': 5, 'июнь': 6, 'июль': 7, 'август': 8,
            'сентябрь': 9, 'октябрь': 10, 'ноябрь': 11, 'декабрь': 12
        }
        return months.get(month_name.lower(), 1)
