from PyQt6.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QVBoxLayout, QHBoxLayout,
                             QPushButton, QMenu, QApplication, QToolTip,
                             QFrame, QScrollArea, QLineEdit, QInputDialog)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QDate, QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QAction, QIcon, QBrush, QIntValidator
from datetime import datetime
import calendar

QApplication.setStyle("Fusion")
QApplication.setPalette(QApplication.style().standardPalette())

from frontend.styles import DayTypes
from frontend.config import UIConfig

# ----------------------------------------------------------------------------------------------------------

# Ячейки дня в табеле
class DayCellWidget(QPushButton):
    clicked_left = pyqtSignal(tuple)  # (emp_idx, day)
    clicked_right = pyqtSignal(tuple)  # (emp_idx, day)
    hours_changed = pyqtSignal(tuple, int)  # (emp_idx, day), hours
    
    def __init__(self, emp_idx, day, code, hours=0, parent=None):
        super().__init__(parent)
        self.emp_idx = emp_idx
        self.day = day
        self.code = code
        self.hours = hours
        self.editing = False
        self.line_edit = None
        
        self.setFixedSize(UIConfig.CELL_WIDTH, UIConfig.CELL_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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
    
    def update_style(self):
        # Если код пустой, используем EMPTY (пробел)
        code_to_use = self.code if self.code and self.code.strip() else DayTypes.EMPTY
        
        name, color, short_code = DayTypes.TYPES[code_to_use]
        
        # Установка цвета фона
        self.setStyleSheet(self.styleSheet() + f"""
            QPushButton {{
                background-color: {color};
            }}
        """)
        
        # Установка текста
        if self.code == DayTypes.WORKDAY and self.hours > 0:
            # Для рабочих дней показываем часы
            display_text = f"{self.hours}"
        else:
            # Для остальных типов показываем код
            if self.code and self.code != DayTypes.EMPTY:
                display_text = short_code
            else:
                display_text = ""
        
        self.setText(display_text)
    
    # Установка нового кода дня и часов
    def set_code(self, code, hours=0):
        # Если код пустой, используем EMPTY
        self.code = code if code and code.strip() else DayTypes.EMPTY
        self.hours = hours
        self.update_style()
    
    # Обработка нажатия мыши
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_left.emit((self.emp_idx, self.day))
        elif event.button() == Qt.MouseButton.RightButton:
            self.clicked_right.emit((self.emp_idx, self.day))
        super().mousePressEvent(event)
    
    # Обработка двойного клика - начало редактирования
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_editing()
        super().mouseDoubleClickEvent(event)
    
    # Начать редактирование часов
    def start_editing(self):
        if self.editing:
            return
        
        self.editing = True
        
        # Скрываем кнопку
        self.hide()
        
        # Создаем поле ввода
        self.line_edit = QLineEdit(self.parent())
        self.line_edit.setGeometry(self.geometry())
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_edit.setValidator(QIntValidator(0, 24))
        self.line_edit.setText(str(self.hours) if self.hours > 0 else "")
        self.line_edit.setPlaceholderText("часы")
        self.line_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #2196F3;
                border-radius: 3px;
                font-weight: bold;
                font-size: 11px;
                padding: 2px;
                background-color: white;
            }
        """)
        
        # Подключаем сигналы
        self.line_edit.editingFinished.connect(self.finish_editing)
        self.line_edit.returnPressed.connect(self.finish_editing)
        
        self.line_edit.show()
        self.line_edit.setFocus()
        self.line_edit.selectAll()
    
    # Завершить редактирование
    def finish_editing(self):
        if not self.editing or not self.line_edit:
            return
    
        text = self.line_edit.text().strip()
        hours = int(text) if text else 0
        
        # Скрываем и удаляем поле ввода
        self.line_edit.hide()
        self.line_edit.deleteLater()
        self.line_edit = None
        
        if hours != self.hours:
            self.hours_changed.emit((self.emp_idx, self.day), hours)
        elif hours > 0 and self.code != DayTypes.WORKDAY:
            self.hours_changed.emit((self.emp_idx, self.day), hours)
        
        # Показываем кнопку
        self.show()
        self.editing = False
    
    # Обработка нажатий клавиш
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if not self.editing:
                self.start_editing()
        else:
            super().keyPressEvent(event)

# ----------------------------------------------------------------------------------------------------------

# Таблица календаря табеля
class CalendarTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.day_cells = {}  # (emp_idx, day): DayCellWidget
        self.setup_ui()

        self.setAutoScroll(False)
        
        # Запрещаем редактирование ячеек двойным щелчком
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    
    def setup_ui(self):
        # Настройка таблицы
        self.setAlternatingRowColors(False)
        self.setShowGrid(True)
        self.setGridStyle(Qt.PenStyle.SolidLine)
        self.setWordWrap(True)
        
        # Настройка заголовков
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
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
        emp_header.setForeground(QBrush(QColor('#FFFFFF')))
        emp_header.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        emp_header.setFont(font)
        self.setItem(0, 0, emp_header)
        
        # Создание заголовков дней
        for day in range(1, days_in_month + 1):
            date_obj = datetime(year, month, day)
            weekday_num = date_obj.weekday()
            
            day_name_short = russian_days_short[weekday_num]
            is_weekend = weekday_num >= 5
            
            header_text = f"{day}\n{day_name_short}"
            header_item = QTableWidgetItem(header_text)
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if is_weekend:
                header_item.setBackground(QBrush(QColor('#FFEBEE')))
                header_item.setForeground(QBrush(QColor('#C62828')))
            else:
                header_item.setBackground(QBrush(QColor('#E3F2FD')))
                header_item.setForeground(QBrush(QColor('#1565C0')))
            
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
                cell_data = day_data.get(day_key, {'code': DayTypes.EMPTY, 'hours': 0})
                
                current_code = cell_data if isinstance(cell_data, str) else cell_data.get('code', DayTypes.EMPTY)
                # Если код пустой, используем EMPTY
                if not current_code or not current_code.strip():
                    current_code = DayTypes.EMPTY
                current_hours = 0 if isinstance(cell_data, str) else cell_data.get('hours', 0)
                
                cell_widget = DayCellWidget(emp_idx, day, current_code, current_hours)
                self.setCellWidget(row, day, cell_widget)
                self.day_cells[day_key] = cell_widget
        
        self.day_cells_updated = self.day_cells
    
    # Обновление ячейки дня
    def update_day_cell(self, emp_idx, day, code, hours=0):
        day_key = (emp_idx, day)
        if day_key in self.day_cells:
            self.day_cells[day_key].set_code(code, hours)
    
    # Очистка календаря
    def clear_calendar(self):
        self.day_cells.clear()
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)

# ----------------------------------------------------------------------------------------------------------

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
