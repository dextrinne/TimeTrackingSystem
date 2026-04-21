import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
import calendar
from pathlib import Path

from frontend.styles import DayTypes
from frontend.config import AppConfig


class TemplateExporter:
    """Класс для экспорта табеля в Excel"""
    
    def __init__(self):
        self.ensure_export_dir()
    
    def ensure_export_dir(self):
        """Создание директории для экспорта"""
        export_dir = Path.home() / "Documents" / "Табели"
        export_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir = export_dir
    
    def export_timetable(self, year, month, employees, day_data, with_stats=True, with_colors=True):
        """Экспорт табеля в Excel"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Табель {AppConfig.MONTHS[month-1]} {year}"
        
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Стили
        header_fill = PatternFill(start_color="2196F3", end_color="2196F3", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True, size=11)
        center_alignment = Alignment(horizontal="center", vertical="center")
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Заголовок
        ws.merge_cells(f'A1:{get_column_letter(days_in_month + 2)}1')
        title_cell = ws['A1']
        title_cell.value = f"ТАБЕЛЬ УЧЕТА РАБОЧЕГО ВРЕМЕНИ ЗА {AppConfig.MONTHS[month-1].upper()} {year} г."
        title_cell.font = Font(bold=True, size=14)
        title_cell.alignment = center_alignment
        
        # Шапка таблицы
        headers = ['№', 'ФИО', 'Должность']
        for day in range(1, days_in_month + 1):
            headers.append(str(day))
        
        if with_stats:
            headers.extend(['Рабочие', 'Выходные', 'Отпуск', 'Больничный', 'Прочее'])
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=2, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_alignment
            cell.border = border
        
        # Данные сотрудников
        for emp_idx, employee in enumerate(employees, 1):
            row = emp_idx + 2
            
            # Номер
            ws.cell(row=row, column=1, value=emp_idx).border = border
            
            # ФИО
            ws.cell(row=row, column=2, value=employee.get('name', '')).border = border
            
            # Должность
            ws.cell(row=row, column=3, value=employee.get('position', '')).border = border
            
            # Статистика
            stats = {
                'working_days': 0,
                'weekends': 0,
                'vacation': 0,
                'sick_leave': 0,
                'other': 0
            }
            
            # Дни месяца
            for day in range(1, days_in_month + 1):
                day_key = (emp_idx - 1, day)
                code = day_data.get(day_key, DayTypes.EMPTY)
                name, color, short_code = DayTypes.TYPES[code]
                
                cell = ws.cell(row=row, column=day + 3, value=short_code)
                cell.alignment = center_alignment
                cell.border = border
                
                if with_colors and code != DayTypes.EMPTY:
                    cell.fill = PatternFill(start_color=color[1:], end_color=color[1:], fill_type="solid")
                
                # Статистика
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
            
            # Добавление статистики
            if with_stats:
                col_offset = days_in_month + 4
                ws.cell(row=row, column=col_offset, value=stats['working_days']).border = border
                ws.cell(row=row, column=col_offset + 1, value=stats['weekends']).border = border
                ws.cell(row=row, column=col_offset + 2, value=stats['vacation']).border = border
                ws.cell(row=row, column=col_offset + 3, value=stats['sick_leave']).border = border
                ws.cell(row=row, column=col_offset + 4, value=stats['other']).border = border
        
        # Автоподбор ширины столбцов
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 12
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 25
        
        # Сохранение файла
        filename = self.export_dir / f"Табель_{AppConfig.MONTHS[month-1]}_{year}.xlsx"
        wb.save(filename)
        
        return str(filename)