#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Стили и цветовые схемы приложения
"""

class DayTypes:
    """Типы дней и их визуальное представление"""
    
    # Основные типы дней (часто используемые)
    WORKDAY = 'Р'          # Рабочий день
    WEEKEND = 'В'          # Выходные и нерабочие праздничные дни
    NIGHT = 'Н'            # Работа в ночное время
    SICK = 'Б'             # Временная нетрудоспособность
    PREGNANCY = 'Р'        # Отпуск по беременности и родам (используем 'Р' как рабочий)
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
    
    # Словарь с описанием и цветами
    TYPES = {
        EMPTY: ('Пусто', '#FFFFFF', ''),
        WORKDAY: ('Рабочий день', '#90EE90', 'Р'),
        WEEKEND: ('Выходные и праздничные дни', '#87CEEB', 'В'),
        NIGHT: ('Работа в ночное время', '#4A90E2', 'Н'),
        SICK: ('Временная нетрудоспособность', '#FFB6C1', 'Б'),
        VACATION_MAIN: ('Ежегодный оплачиваемый отпуск', '#FFD700', 'ОТ'),
        VACATION_EXTRA: ('Дополнительный отпуск', '#FFA500', 'ОД'),
        STUDY: ('Отпуск в связи с обучением', '#9ACD32', 'У'),
        UNPAID: ('Отпуск без сохранения ЗП', '#DDA0DD', 'ДО'),
        NONWORK_PAID: ('Нерабочие оплачиваемые дни', '#98FB98', 'НОД'),
        ABSENTEEISM: ('Прогулы', '#FF6347', 'ПР'),
        BUSINESS_TRIP: ('Служебная командировка', '#FF8C00', 'К'),
        UNKNOWN: ('Неявки по невыясненным причинам', '#A9A9A9', 'НН'),
        ADMIN_PERMIT: ('Неявки с разрешения администрации', '#B0C4DE', 'А'),
        WEEKEND_WORK: ('Работа в выходные дни', '#32CD32', 'РП'),
        STATE_DUTY: ('Выполнение гособязанностей', '#8B4513', 'Г'),
        OVERTIME: ('Сверхурочная работа', '#FF4500', 'С'),
        CHILD_CARE: ('Отпуск по уходу за ребенком', '#FF69B4', 'ОЖ'),
        TRANSITION: ('Дни до/после должности', '#D3D3D3', 'Х'),
    }
    
    # Основные типы для быстрого переключения (левый клик)
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
        'Рабочее время': [WORKDAY, NIGHT, WEEKEND_WORK, OVERTIME],
        'Отпуска': [VACATION_MAIN, VACATION_EXTRA, STUDY, UNPAID, CHILD_CARE],
        'Отсутствия': [SICK, ABSENTEEISM, UNKNOWN, ADMIN_PERMIT, STATE_DUTY, TRANSITION],
        'Прочее': [WEEKEND, NONWORK_PAID, BUSINESS_TRIP]
    }
    
    # Порядок при левом клике
    ORDER = MAIN_TYPES


class Colors:
    """Цветовая схема приложения"""
    
    # Основные цвета
    WHITE = '#FFFFFF'
    TEXT = '#000000'
    
    # Цвета интерфейса
    HEADER_BG = '#D3D3D3'
    WEEKEND_HEADER = '#E0E0E0'
    EMPLOYEE_BG = '#F0F0F0'
    
    # Цвета статусов
    SUCCESS = '#28A745'
    INFO = '#007BFF'
    WARNING = '#FFC107'
    ERROR = '#DC3545'
    
    # Цвета кнопок
    BUTTON_BG = '#E0E0E0'
    BUTTON_ACTIVE = '#C0C0C0'
    
    # Цвета для группировки в меню
    MENU_GROUP_WORK = '#90EE90'
    MENU_GROUP_VACATION = '#FFD700'
    MENU_GROUP_ABSENCE = '#FFB6C1'
    MENU_GROUP_OTHER = '#DDA0DD'


class Fonts:
    """Шрифты приложения"""
    
    # Размеры шрифтов
    SMALL = ("Arial", 8)
    NORMAL = ("Arial", 9)
    BOLD = ("Arial", 9, "bold")
    LARGE = ("Arial", 10)
    HEADER = ("Arial", 9, "bold")
    DAY_BUTTON = ("Arial", 9, "bold")
    DAY_HEADER = ("Arial", 8)
    TOOLTIP = ("Arial", 8)