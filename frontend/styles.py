class DayTypes:
    # Основные типы дней (часто используемые)
    WORKDAY = '2'          # Рабочий день (надо изменить)
    WEEKEND = 'В'          # Выходные и нерабочие праздничные дни
    NIGHT = 'Н'            # Работа в ночное время
    SICK = 'Б'             # Временная нетрудоспособность
    PREGNANCY = 'Р'        # Отпуск по беременности и родам 
    VACATION_MAIN = 'ОТ'   # Ежегодный оплачиваемый отпуск
    VACATION_EXTRA = 'ОД'  # Ежегодный дополнительный оплачиваемый отпуск
    STUDY = 'У'            # Дополнительный отпуск в связи с обучением
    UNPAID = 'ДО'          # Отпуск без сохранения заработной платы
    NONWORK_PAID = 'НОД'   # Нерабочие оплачиваемые дни
    ABSENTEEISM = 'ПР'     # Прогулы
    BUSINESS_TRIP = 'К'    # Служебная командировка
    UNKNOWN = 'НН'         # Неявки по невыясненным причинам
    ADMIN_PERMIT = 'А'     # Неявки с разрешения администрации
    WEEKEND_WORK = 'РП'    # Работа в выходные и нерабочие праздничные дни
    STATE_DUTY = 'Г'       # Выполнение гособязанностей
    OVERTIME = 'С'         # Продолжительность сверхурочной работы
    CHILD_CARE = 'ОЖ'      # Отпуск по уходу за ребенком до 3 лет
    TRANSITION = 'Х'       # Дни до вступления/после освобождения от должности
    EMPTY = ' '            # Пусто
    
    # Словарь с описанием и цветами (более современная палитра)
    TYPES = {
        EMPTY: ('Пусто', '#FFFFFF', ''),
        WORKDAY: ('Рабочий день', '#4CAF50', 'Р'),
        WEEKEND: ('Выходные и праздничные дни', '#64B5F6', 'В'),
        NIGHT: ('Работа в ночное время', '#3F51B5', 'Н'),
        SICK: ('Временная нетрудоспособность', '#EF5350', 'Б'),
        VACATION_MAIN: ('Ежегодный оплачиваемый отпуск', '#FFCA28', 'ОТ'),
        VACATION_EXTRA: ('Дополнительный отпуск', '#FF9800', 'ОД'),
        STUDY: ('Отпуск в связи с обучением', '#8BC34A', 'У'),
        UNPAID: ('Отпуск без сохранения ЗП', '#CE93D8', 'ДО'),
        NONWORK_PAID: ('Нерабочие оплачиваемые дни', '#81C784', 'НОД'),
        ABSENTEEISM: ('Прогулы', '#FF5722', 'ПР'),
        BUSINESS_TRIP: ('Служебная командировка', '#FF7043', 'К'),
        UNKNOWN: ('Неявки по невыясненным причинам', '#90A4AE', 'НН'),
        ADMIN_PERMIT: ('Неявки с разрешения администрации', '#78909C', 'А'),
        WEEKEND_WORK: ('Работа в выходные дни', '#66BB6A', 'РП'),
        STATE_DUTY: ('Выполнение гособязанностей', '#8D6E63', 'Г'),
        OVERTIME: ('Сверхурочная работа', '#FF5252', 'С'),
        CHILD_CARE: ('Отпуск по уходу за ребенком', '#F06292', 'ОЖ'),
        TRANSITION: ('Дни до/после должности', '#BDBDBD', 'Х'),
    }
    
    # Основные типы 
    MAIN_TYPES = [
        EMPTY,
        WORKDAY,
        WEEKEND,
        VACATION_MAIN,
        SICK,
        BUSINESS_TRIP,
    ]
    
    # Группировка типов для контекстного меню
    TYPE_GROUPS = {
        'Рабочее время': [ NIGHT, WEEKEND_WORK, OVERTIME],
        'Отпуска': [VACATION_MAIN, VACATION_EXTRA, STUDY, UNPAID, CHILD_CARE],
        'Отсутствия': [SICK, ABSENTEEISM, UNKNOWN, ADMIN_PERMIT, STATE_DUTY, TRANSITION],
        'Прочее': [WEEKEND, NONWORK_PAID, BUSINESS_TRIP]
    }
    
    # Порядок при левом клике
    ORDER = MAIN_TYPES

# ----------------------------------------------------------------------------------------------------------

class AppStyle:
    @staticmethod
    def get_stylesheet():
        return """
            /* ОБЩИЕ СТИЛИ ПРИЛОЖЕНИЯ */
            QMainWindow {
                background-color: #F8F9FB; /* Фон как у вкладок, чтобы не было серых углов */
            }

            QWidget {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 12px;
            }

            /* ВЕРХНЯЯ ИНФО-ПАНЕЛЬ (задан в коде, оставляем как есть) */

            /* ПАНЕЛЬ ВКЛАДОК (QTabWidget) */
            QTabWidget::pane {
                border: 1px solid #C5D5EA;
                border-radius: 0 0 5px 5px;
                background: #F8F9FB;
                margin-top: -1px; /* Убираем двойную границу с вкладкой */
            }

            QTabBar::tab {
                background: #E1ECF7;
                color: #3B5E8B;
                font-weight: bold;
                padding: 10px 25px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid #C5D5EA;
                border-bottom: none;
            }

            QTabBar::tab:selected {
                background: #F8F9FB;
                color: #0D47A1;
                border-bottom: 2px solid #F8F9FB; /* Скрываем нижнюю границу панели */
            }

            QTabBar::tab:hover:!selected {
                background: #D0E2F3;
                color: #0D47A1;
            }

            /* ТАБЛИЦЫ (QTableWidget, QTreeWidget) */
            QTableWidget, QTreeWidget {
                background-color: white;
                alternate-background-color: #F4F8FC;
                border: 1px solid #C5D5EA;
                border-radius: 5px;
                gridline-color: #D9E6F2;
                outline: none;
            }
            
            /* ЯВНЫЕ СТИЛИ ДЛЯ ВЫДЕЛЕННЫХ ЭЛЕМЕНТОВ */
            QTableWidget::item:selected, QTreeWidget::item:selected {
                background-color: #71A5DE;
                color: white;
            }
            
            /* Стиль для неактивного выделения (когда фокус на другом виджете) */
            QTableWidget::item:selected:!active, QTreeWidget::item:selected:!active {
                background-color: #A0C0DF;
                color: #2C3E50;
            }

            QTableWidget::item, QTreeWidget::item {
                padding: 8px 5px;
                border-bottom: 1px solid #E1ECF7;
            }
            
            /* Стиль при наведении */
            QTableWidget::item:hover, QTreeWidget::item:hover {
                background-color: #E1ECF7;
            }
            
            QHeaderView::section {
                background-color: #E1ECF7;
                color: #2C3E50;
                font-weight: bold;
                padding: 10px 5px;
                border: none;
                border-right: 1px solid #C5D5EA;
                border-bottom: 2px solid #71A5DE;
            }
            
            QHeaderView::section:last {
                border-right: none;
            }
            

            /* СКРОЛЛБАРЫ (QScrollArea, QScrollBar) */
            QScrollBar:vertical {
                border: none;
                background: #F0F4F8;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #A0C0DF;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #71A5DE;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }

            QScrollBar:horizontal {
                border: none;
                background: #F0F4F8;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #A0C0DF;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #71A5DE;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }

            /* КНОПКИ (QPushButton) */
            QPushButton {
                background-color: #E1ECF7;
                color: #2C3E50;
                border: 1px solid #B0C9E0;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #D0E2F3;
                border: 1px solid #71A5DE;
                color: #0D47A1;
            }
            QPushButton:pressed {
                background-color: #71A5DE;
                color: white;
                border: 1px solid #4A86C8;
            }
            QPushButton:disabled {
                background-color: #E0E7EF;
                color: #8C9EB2;
                border: 1px solid #C5D5EA;
            }

            /* ГРУППИРОВКА (QGroupBox) */
            QGroupBox {
                font-weight: bold;
                color: #0D47A1;
                border: 1px solid #C5D5EA;
                border-radius: 6px;
                margin-top: 1.5ex;
                padding-top: 10px;
                background-color: #F8F9FB;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: #F8F9FB;
            }

            /* СПИНБОКСЫ И КОМБОБОКСЫ (уже были, немного доработаны) */
            QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: white;
                color: #2C3E50;
                border: 1px solid #B0C9E0;
                border-radius: 4px;
                padding: 6px 10px;
                min-height: 20px;
                font-weight: normal;
                selection-background-color: #71A5DE;
            }
            QComboBox:hover, QSpinBox:hover {
                border: 1px solid #71A5DE;
            }
            QComboBox:focus, QSpinBox:focus {
                border: 2px solid #4A86C8;
            }
            

            /* СТРОКИ ВВОДА (QLineEdit) */
            QLineEdit {
                background-color: white;
                color: #2C3E50;
                border: 1px solid #B0C9E0;
                border-radius: 4px;
                padding: 8px 10px;
                selection-background-color: #71A5DE;
            }
            QLineEdit:focus {
                border: 2px solid #4A86C8;
            }

            QStatusBar {
                background-color: #E1ECF7;
                color: #2C3E50;
                border-top: 1px solid #C5D5EA;
                font-weight: normal;
            }
            QStatusBar::item {
                border: none;
            }

            /* ТУЛБАР (основной) */
            QToolBar {
                background-color: #71A5DE;
                border: none;
                spacing: 8px;
                padding: 6px;
            }
            QToolBar QToolButton {
                color: white;
                font-weight: bold;
                padding: 6px 15px;
                border-radius: 4px;
                background-color: transparent;
            }
            QToolBar QToolButton:hover {
                background-color: #5A95CC;
            }
            QToolBar QToolButton:pressed {
                background-color: #4A86C8;
            }
            QToolBar QLabel {
                color: white;
                font-weight: bold;
                margin-left: 5px;
            }
            QToolBar::separator {
                width: 2px;
                background-color: rgba(255, 255, 255, 0.3);
                margin: 4px 5px;
            }


            /* СТИЛИ ДЛЯ QComboBox И ЕГО ВЫПАДАЮЩЕГО СПИСКА */
            QComboBox {
                background-color: white;
                color: #2C3E50;
                border: 1px solid #B0C9E0;
                border-radius: 4px;
                padding: 6px 10px;
                min-height: 20px;
            }
            
            QComboBox:hover {
                border: 1px solid #71A5DE;
            }
            
            QComboBox:focus {
                border: 2px solid #4A86C8;
            }
            
            
            
            /* СТИЛИ ДЛЯ ВЫПАДАЮЩЕГО СПИСКА */
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2C3E50;
                border: 1px solid #B0C9E0;
                border-radius: 4px;
                selection-background-color: #71A5DE;
                selection-color: white;
                outline: none;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 6px 10px;
                min-height: 25px;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #E1ECF7;
                color: #0D47A1;
            }

            
        """