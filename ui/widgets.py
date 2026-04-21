from PyQt6.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QVBoxLayout, QHBoxLayout,
                             QPushButton, QMenu, QApplication, QToolTip,
                             QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QDate, QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QAction, QIcon, QBrush
from datetime import datetime
import calendar

QApplication.setStyle("Fusion")
QApplication.setPalette(QApplication.style().standardPalette())

from frontend.styles import DayTypes
from frontend.config import UIConfig

# Ячейки дня в табеле
class DayCellWidget(QPushButton):
    clicked_left = pyqtSignal(tuple)  # (emp_idx, day)
    clicked_right = pyqtSignal(tuple)  # (emp_idx, day)
    
    def __init__(self, emp_idx, day, code, parent=None):
        super().__init__(parent)
        self.emp_idx = emp_idx
        self.day = day
        self.code = code
        
        self.setFixedSize(UIConfig.CELL_WIDTH, UIConfig.CELL_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Настройка стиля
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #E0E0E0;
                border-radius: 3px;
                font-weight: bold;
                font-size: 11px;
                padding: 2px;
            }
            QPushButton:hover {
                border: 2px solid #2196F3;
            }
        """)
        
        self.update_style()
    
    # Обновление стиля кнопки
    def update_style(self):
        name, color, short_code = DayTypes.TYPES[self.code]
        
        # Установка цвета фона
        self.setStyleSheet(self.styleSheet() + f"""
            QPushButton {{
                background-color: {color};
            }}
        """)
        
        # Установка текста
        display_text = short_code if self.code != DayTypes.EMPTY else ""
        self.setText(display_text)
        
        # Установка тултипа
        # self.setToolTip(name)
    
    def set_code(self, code):
        """Установка нового кода дня"""
        self.code = code
        self.update_style()
    
    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_left.emit((self.emp_idx, self.day))
        elif event.button() == Qt.MouseButton.RightButton:
            self.clicked_right.emit((self.emp_idx, self.day))
        super().mousePressEvent(event)

# Таблица календаря табеля
class CalendarTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.day_cells = {}  # (emp_idx, day): DayCellWidget
        self.setup_ui()
    
    def setup_ui(self):
        # Настройка таблицы
        self.setAlternatingRowColors(False)
        self.setShowGrid(True)
        self.setGridStyle(Qt.PenStyle.SolidLine)
        self.setWordWrap(True)
        
        # Настройка заголовков
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verticalHeader().setVisible(False)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        
        # Стиль
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 0px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
                font-size: 11px;
            }
        """)
    
    def create_calendar(self, year, month, employees, day_data):
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Русские названия дней недели
        russian_days_full = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        russian_days_short = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        
        # Настройка размеров таблицы
        self.setColumnCount(days_in_month + 1)  # +1 для колонки сотрудников
        self.setRowCount(len(employees) + 1)    # +1 для заголовков дней
        
        # Установка ширины колонок
        self.setColumnWidth(0, UIConfig.EMPLOYEE_COLUMN_WIDTH)
        for day in range(1, days_in_month + 1):
            self.setColumnWidth(day, UIConfig.CELL_WIDTH)
        
        # Создание заголовка сотрудников
        emp_header = QTableWidgetItem("Сотрудник / Должность")
        emp_header.setBackground(QBrush(QColor('#212529')))
        emp_header.setForeground(QBrush(QColor('#FFFFFF')))  # Белый текст для лучшей читаемости
        emp_header.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        emp_header.setFont(font)
        self.setItem(0, 0, emp_header)
        
        # Создание заголовков дней с русскими названиями
        for day in range(1, days_in_month + 1):
            # Получаем день недели для текущей даты (0 = понедельник, 6 = воскресенье)
            # В Python: date.weekday() где понедельник = 0, воскресенье = 6
            date_obj = datetime(year, month, day)
            weekday_num = date_obj.weekday()  # 0-6, где 0 = понедельник
            
            # Получаем русское название дня недели
            day_name_short = russian_days_short[weekday_num]
            day_name_full = russian_days_full[weekday_num]
            
            # Определяем выходной (суббота = 5, воскресенье = 6)
            is_weekend = weekday_num >= 5  # 5 = суббота, 6 = воскресенье
            
            # Формируем текст заголовка: номер дня и сокращенное название
            header_text = f"{day}\n{day_name_short}"
            header_item = QTableWidgetItem(header_text)
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Устанавливаем цвет фона для выходных дней
            if is_weekend:
                header_item.setBackground(QBrush(QColor('#FFEBEE')))  # Светло-красный для выходных
                header_item.setForeground(QBrush(QColor('#C62828')))  # Темно-красный текст
            else:
                header_item.setBackground(QBrush(QColor('#E3F2FD')))  # Светло-голубой для рабочих дней
                header_item.setForeground(QBrush(QColor('#1565C0')))  # Синий текст
            
            # Устанавливаем тултип с полным названием дня
            # header_item.setToolTip(day_name_full)
            
            font = QFont()
            font.setBold(True)
            header_item.setFont(font)
            self.setItem(0, day, header_item)
        
        # Установка высоты строк
        self.setRowHeight(0, 50)
        for row in range(1, len(employees) + 1):
            self.setRowHeight(row, UIConfig.CELL_HEIGHT)
        
        # Создание строк сотрудников
        for emp_idx, employee in enumerate(employees):
            row = emp_idx + 1
            
            # Ячейка с информацией о сотруднике
            emp_info = f"{employee.get('name', '')}\n{employee.get('position', '')}"
            emp_item = QTableWidgetItem(emp_info)
            emp_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            emp_item.setBackground(QBrush(QColor('#F8F9FA')))
            
            font = QFont()
            font.setPointSize(10)
            emp_item.setFont(font)
            
            self.setItem(row, 0, emp_item)
            
            # Ячейки дней
            for day in range(1, days_in_month + 1):
                day_key = (emp_idx, day)
                current_code = day_data.get(day_key, DayTypes.EMPTY)
                
                cell_widget = DayCellWidget(emp_idx, day, current_code)
                self.setCellWidget(row, day, cell_widget)
                self.day_cells[day_key] = cell_widget
        
        self.day_cells_updated = self.day_cells
    
    # Обновление ячейки дня
    def update_day_cell(self, emp_idx, day, code):
        day_key = (emp_idx, day)
        if day_key in self.day_cells:
            self.day_cells[day_key].set_code(code)
    
    # Очистка календаря
    def clear_calendar(self):
        self.day_cells.clear()
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)


# Карточка с информацией о сотруднике
class EmployeeInfoCard(QFrame):
    def __init__(self, employee, parent=None):
        super().__init__(parent)
        self.employee = employee
        self.setup_ui()
    
    def setup_ui(self):
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Имя сотрудника
        name_label = QLabel(self.employee.get('name', ''))
        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #212121;")
        layout.addWidget(name_label)
        
        # Должность
        position_label = QLabel(self.employee.get('position', ''))
        position_font = QFont()
        position_font.setPointSize(11)
        position_label.setFont(position_font)
        position_label.setStyleSheet("color: #757575;")
        layout.addWidget(position_label)
        
        # Ставка
        rate_label = QLabel(f"Ставка: {self.employee.get('rate', 1.0)}")
        rate_label.setStyleSheet("color: #2196F3; font-weight: bold; margin-top: 8px;")
        layout.addWidget(rate_label)
        
        self.setLayout(layout)