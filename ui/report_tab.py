"""
Вкладка формирования отчётов на tkinter.
ЛР1-Ф4,Ф5: Генерация отчётов, выгрузка в XLSX.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from services.report_service import ReportService
from services.timesheet_service import TimesheetService


class ReportTab(ttk.Frame):
    """Вкладка отчётов."""

    def __init__(self, parent, db_manager, current_user):
        super().__init__(parent)
        self.db = db_manager
        self.current_user = current_user
        self.report_service = ReportService(db_manager)
        self.timesheet_service = TimesheetService(db_manager)
        self.current_timesheet_id = None
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        # Панель действий
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(action_frame, text='Выберите табель:').pack(side=tk.LEFT, padx=5)
        self.timesheet_combo = ttk.Combobox(action_frame, state='readonly', width=30)
        self.load_timesheets()
        self.timesheet_combo.pack(side=tk.LEFT, padx=5)
        self.timesheet_combo.bind('<<ComboboxSelected>>', self.on_timesheet_changed)

        ttk.Button(action_frame, text='📊 Сформировать отчёт', command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text='💾 Экспорт в XLSX', command=self.export_to_xlsx).pack(side=tk.LEFT, padx=5)

        # Таблица отчёта
        report_frame = ttk.LabelFrame(self, text='Сводный отчёт по табелю')
        report_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ('num', 'fio', 'position', 'norm_hours', 'workdays', 
                   'vacations', 'sick_leaves', 'business_trips', 'absences', 'total_hours')
        self.tree = ttk.Treeview(report_frame, columns=columns, show='headings')
        
        self.tree.heading('num', text='№')
        self.tree.heading('fio', text='ФИО')
        self.tree.heading('position', text='Должность')
        self.tree.heading('norm_hours', text='Норма часов')
        self.tree.heading('workdays', text='Рабочие дни')
        self.tree.heading('vacations', text='Отпуск')
        self.tree.heading('sick_leaves', text='Больничный')
        self.tree.heading('business_trips', text='Командировка')
        self.tree.heading('absences', text='Неявка')
        self.tree.heading('total_hours', text='Всего часов')
        
        self.tree.column('num', width=40, anchor=tk.CENTER)
        self.tree.column('fio', width=250)
        self.tree.column('position', width=150)
        for col in ['norm_hours', 'workdays', 'vacations', 'sick_leaves', 'business_trips', 'absences', 'total_hours']:
            self.tree.column(col, width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def load_timesheets(self):
        """Загрузка списка табелей."""
        timesheets = self.timesheet_service.get_all_timesheets()
        values = []
        self.timesheet_ids = []
        
        for ts in timesheets:
            display = f"{ts.period_start} — {ts.period_end} ({ts.status})"
            values.append(display)
            self.timesheet_ids.append(ts.id_timesheet)
        
        self.timesheet_combo['values'] = values
        if values:
            self.timesheet_combo.current(0)
            self.current_timesheet_id = self.timesheet_ids[0]

    def on_timesheet_changed(self, event):
        """Обработка изменения выбранного табеля."""
        idx = self.timesheet_combo.current()
        if idx >= 0:
            self.current_timesheet_id = self.timesheet_ids[idx]

    def generate_report(self):
        """Формирование отчёта."""
        if not self.current_timesheet_id:
            messagebox.showwarning('Ошибка', 'Выберите табель')
            return

        report_data = self.report_service.get_timesheet_report(self.current_timesheet_id)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for row, data in enumerate(report_data):
            self.tree.insert('', tk.END, values=(
                row + 1,
                data['fio'],
                data['position'],
                data['norm_hours'],
                data['workdays'],
                data['vacations'],
                data['sick_leaves'],
                data['business_trips'],
                data['absences'],
                f"{data['total_hours']:.2f}"
            ))

        messagebox.showinfo('Успех', f'Отчёт сформирован ({len(report_data)} сотрудников)')

    def export_to_xlsx(self):
        """Экспорт в XLSX."""
        if not self.current_timesheet_id:
            messagebox.showwarning('Ошибка', 'Выберите табель')
            return

        file_path = filedialog.asksaveasfilename(
            title='Сохранить отчёт',
            defaultextension='.xlsx',
            filetypes=[('Excel Files', '*.xlsx')],
            initialfile=f'tabel_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
        if file_path:
            success = self.report_service.export_to_xlsx(self.current_timesheet_id, file_path)
            if success:
                messagebox.showinfo('Успех', f'Отчёт экспортирован:\n{file_path}')
            else:
                messagebox.showwarning('Ошибка', 'Не удалось экспортировать отчёт')
