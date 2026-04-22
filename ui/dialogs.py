from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFormLayout,
                             QDoubleSpinBox, QGroupBox, QDialogButtonBox,
                             QApplication, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QIcon, QPixmap, QPainter, QColor

from frontend.styles import AppStyle, DayTypes
from frontend.config import AppConfig
from pathlib import Path

# ----------------------------------------------------------------------------------------------------------

class ModernDialog(QDialog):
    def __init__(self, parent=None, title="Диалог"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setStyleSheet(AppStyle.get_stylesheet())
        
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)


class EmployeeDialog(ModernDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent, "Добавить сотрудника" if employee is None else "Редактировать сотрудника")
        self.employee = employee
        self.result = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        title_label = QLabel("Информация о сотруднике")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: #000000; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите фамилию, имя и отчество")
        self.name_input.setMinimumHeight(35)
        form_layout.addRow("ФИО:", self.name_input)
        
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Введите должность")
        self.position_input.setMinimumHeight(35)
        form_layout.addRow("Должность:", self.position_input)
        
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(AppConfig.MIN_RATE, AppConfig.MAX_RATE)
        self.rate_input.setSingleStep(0.1)
        self.rate_input.setValue(AppConfig.DEFAULT_RATE)
        self.rate_input.setMinimumHeight(35)
        self.rate_input.setSuffix(" ставки")
        form_layout.addRow("Ставка:", self.rate_input)
        
        if self.employee:
            self.name_input.setText(self.employee.get('name', ''))
            self.position_input.setText(self.employee.get('position', ''))
            self.rate_input.setValue(self.employee.get('rate', AppConfig.DEFAULT_RATE))
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox()
        save_button = QPushButton("Сохранить")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                min-width: 100px;
                min-height: 35px;
                color: white;
            }
            QPushButton:hover {
                background-color: #388E3C;
                color: white;                  
            }
        """)
        save_button.clicked.connect(self.save_employee)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                min-width: 100px;
                min-height: 35px;
                color: white;                    
            }
            QPushButton:hover {
                background-color: #616161;
                color: white;                    
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_box.addButton(save_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def save_employee(self):
        name = self.name_input.text().strip()
        position = self.position_input.text().strip()
        rate = self.rate_input.value()
        
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

# ----------------------------------------------------------------------------------------------------------

# Контекстное меню для выбора типа дня
class DayTypeContextMenu(QMenu):
    type_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_menu()
        self.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #C5D5EA;
                border-radius: 4px;
                padding: 5px;
                color: #2c3e50;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #71A5DE;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #E0E0E0;
                margin: 5px 10px;
            }
        """)
    
    # Настройка меню с группировкой типов
    def setup_menu(self):
        for group_name, type_codes in DayTypes.TYPE_GROUPS.items():
            # Добавляем заголовок группы
            group_action = QAction(group_name, self)
            group_action.setEnabled(False)
            font = QFont()
            font.setBold(True)
            group_action.setFont(font)
            self.addAction(group_action)
            
            # Добавляем типы дней в группе
            for code in type_codes:
                name, color, short_code = DayTypes.TYPES[code]
                
                action = QAction(f"{short_code} - {name}", self)
                action.setData(code)
                
                # Устанавливаем цветовую индикацию
                action.setIcon(self.create_color_icon(color))
                
                action.triggered.connect(lambda checked, c=code: self.type_selected.emit(c))
                self.addAction(action)
            
            self.addSeparator()

    # Создание иконки с цветом
    def create_color_icon(self, color):
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(color))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(200, 200, 200))
        painter.drawRect(0, 0, 15, 15)
        painter.end()
        
        return QIcon(pixmap)

# ----------------------------------------------------------------------------------------------------------

# Диалог выбора типа дня (старая версия для обратной совместимости)
class DayTypeMenuDialog(ModernDialog):
    day_selected = pyqtSignal(str)
    
    def __init__(self, parent=None, current_code=None):
        super().__init__(parent, "Выберите тип дня")
        self.current_code = current_code
        self.setup_ui()
    
    # Настройка интерфейса
    def setup_ui(self):
        layout = QVBoxLayout()
        
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
    
    # Выбор типа дня
    def select_type(self, code):
        self.day_selected.emit(code)
        self.accept()

# ----------------------------------------------------------------------------------------------------------

class ExportDialog(ModernDialog):
    def __init__(self, parent=None, year=None, month=None):
        super().__init__(parent, "Экспорт табеля в Excel")
        self.year = year
        self.month = month
        self.export_with_stats = True
        self.export_with_colors = True
        self.selected_path = None
        self.setup_ui()
    
    def setup_ui(self):
        from PyQt6.QtWidgets import QCheckBox, QFileDialog, QHBoxLayout
        from pathlib import Path
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Информация о экспорте
        info_label = QLabel(f"Экспорт табеля за {AppConfig.MONTHS[self.month-1]} {self.year} года")
        info_font = QFont()
        info_font.setPointSize(12)
        info_font.setBold(True)
        info_label.setFont(info_font)
        layout.addWidget(info_label)
        
        # Выбор пути сохранения
        path_group = QGroupBox("Путь сохранения")
        path_layout = QVBoxLayout()
        
        path_select_layout = QHBoxLayout()
        self.path_label = QLabel("Файл не выбран")
        self.path_label.setStyleSheet("color: #757575; font-style: italic;")
        self.path_label.setWordWrap(True)
        path_select_layout.addWidget(self.path_label, 1)
        
        browse_button = QPushButton("Обзор...")
        browse_button.clicked.connect(self.browse_path)
        path_select_layout.addWidget(browse_button)
        
        path_layout.addLayout(path_select_layout)
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        
        # Устанавливаем путь по умолчанию
        default_path = Path.home() / "Documents" / f"Табель_{AppConfig.MONTHS[self.month-1]}_{self.year}.xlsx"
        self.selected_path = str(default_path)
        self.path_label.setText(self.selected_path)
        self.path_label.setToolTip(self.selected_path)
        
        layout.addStretch()
        
        # Кнопки
        button_box = QDialogButtonBox()
        
        export_button = QPushButton("Экспортировать")
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                min-width: 100px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #388E3C;
                color: white;
            }
        """)
        export_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                min-width: 100px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #616161;
                color: white;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_box.addButton(export_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        
        # Увеличиваем размер диалога
        self.setMinimumWidth(500)
        self.setMinimumHeight(100)
    
    def browse_path(self):
        """Выбор пути для сохранения"""
        from PyQt6.QtWidgets import QFileDialog
        
        default_name = f"Табель_{AppConfig.MONTHS[self.month-1]}_{self.year}.xlsx"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить табель как",
            self.selected_path or str(Path.home() / "Documents" / default_name),
            "Excel files (*.xlsx);;All files (*.*)"
        )
        
        if file_path:
            # Добавляем расширение если не указано
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            self.selected_path = file_path
            self.path_label.setText(file_path)
            self.path_label.setToolTip(file_path)
    
    # Подтверждение экспорта
    def accept(self):
        if hasattr(self, 'stats_checkbox') and hasattr(self, 'colors_checkbox'):
            self.export_with_stats = self.stats_checkbox.isChecked()
            self.export_with_colors = self.colors_checkbox.isChecked()
        super().accept()