from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFormLayout,
                             QDoubleSpinBox, QGroupBox, QDialogButtonBox,
                             QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from frontend.styles import AppStyle
from frontend.config import AppConfig


class ModernDialog(QDialog):
    def __init__(self, parent=None, title="Диалог"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setStyleSheet(AppStyle.get_stylesheet())
        
        # Установка флага для отключения кнопки "?"
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

# ----------------------------------------------------------------------------------------------------------

# Диалог добавления/редактирования сотрудника
class EmployeeDialog(ModernDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent, "Добавить сотрудника" if employee is None else "Редактировать сотрудника")
        self.employee = employee
        self.result = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title_label = QLabel("Информация о сотруднике")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: #000000; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Форма
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # ФИО
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите фамилию, имя и отчество")
        self.name_input.setMinimumHeight(35)
        form_layout.addRow("ФИО:", self.name_input)
        
        # Должность
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Введите должность")
        self.position_input.setMinimumHeight(35)
        form_layout.addRow("Должность:", self.position_input)
        
        # Ставка
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(AppConfig.MIN_RATE, AppConfig.MAX_RATE)
        self.rate_input.setSingleStep(0.1)
        self.rate_input.setValue(AppConfig.DEFAULT_RATE)
        self.rate_input.setMinimumHeight(35)
        self.rate_input.setSuffix(" ставки")
        form_layout.addRow("Ставка:", self.rate_input)
        
        # Заполнение данными при редактировании
        if self.employee:
            self.name_input.setText(self.employee.get('name', ''))
            self.position_input.setText(self.employee.get('position', ''))
            self.rate_input.setValue(self.employee.get('rate', AppConfig.DEFAULT_RATE))
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_box = QDialogButtonBox()
        save_button = QPushButton("Сохранить")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                min-width: 100px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        save_button.clicked.connect(self.save_employee)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                min-width: 100px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_box.addButton(save_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
# ----------------------------------------------------------------------------------------------------------

    def save_employee(self):
        name = self.name_input.text().strip()
        position = self.position_input.text().strip()
        rate = self.rate_input.value()
        
        # Валидация
        if not name:
            QMessageBox.warning(self, "Ошибка", "Поле 'ФИО' не может быть пустым!")
            self.name_input.setFocus()
            return
        
        if not position:
            QMessageBox.warning(self, "Ошибка", "Поле 'Должность' не может быть пустым!")
            self.position_input.setFocus()
            return
        
        self.result = {
            'name': name,
            'position': position,
            'rate': rate
        }
        
        self.accept()


class DayTypeMenuDialog(ModernDialog):
    """Диалог выбора типа дня"""
    
    day_selected = pyqtSignal(str)
    
    def __init__(self, parent=None, current_code=None):
        super().__init__(parent, "Выберите тип дня")
        self.current_code = current_code
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        from frontend.styles import DayTypes
        
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("Выберите тип дня")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: #000000; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        # Группы типов дней
        for group_name, type_codes in DayTypes.TYPE_GROUPS.items():
            group_box = QGroupBox(group_name)
            group_layout = QVBoxLayout()
            
            for code in type_codes:
                name, color, short_code = DayTypes.TYPES[code]
                
                btn = QPushButton(f"{short_code} - {name}")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: #212121;
                        padding: 10px;
                        border-radius: 4px;
                        text-align: left;
                        font-weight: bold;
                        border: 1px solid #E0E0E0;
                    }}
                    QPushButton:hover {{
                        border: 2px solid #2196F3;
                        background-color: {color};
                    }}
                """)
                
                if code == self.current_code:
                    btn.setStyleSheet(btn.styleSheet() + """
                        QPushButton {
                            border: 3px solid #2196F3;
                        }
                    """)
                
                btn.clicked.connect(lambda checked, c=code: self.select_type(c))
                group_layout.addWidget(btn)
            
            group_box.setLayout(group_layout)
            layout.addWidget(group_box)
        
        # Кнопка отмены
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)
        
        self.setLayout(layout)
    
    def select_type(self, code):
        """Выбор типа дня"""
        self.day_selected.emit(code)
        self.accept()



# ----------------------------------------------------------------------------------------------------------

# Диалог экспорта в Excel
class ExportDialog(ModernDialog):
    def __init__(self, parent=None, year=None, month=None):
        super().__init__(parent, "Экспорт табеля в Excel")
        self.year = year
        self.month = month
        self.export_with_stats = True
        self.export_with_colors = True
        self.setup_ui()
    
    # Настройка интерфейса
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Информация о экспорте
        info_label = QLabel(f"Экспорт табеля за {AppConfig.MONTHS[self.month-1]} {self.year} года")
        info_font = QFont()
        info_font.setPointSize(12)
        info_font.setBold(True)
        info_label.setFont(info_font)
        layout.addWidget(info_label)
        
        # Кнопки
        button_box = QDialogButtonBox()
        export_button = QPushButton("Экспортировать")
        export_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        
        button_box.addButton(export_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        
        layout.addWidget(button_box)
        self.setLayout(layout)