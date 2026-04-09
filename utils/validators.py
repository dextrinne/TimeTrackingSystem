"""
Модуль валидации данных.
ЛР2: Контроль целостности и непротиворечивости данных.
"""

from datetime import date, datetime
from typing import Tuple, Optional


class Validator:
    """Класс для валидации различных данных."""

    @staticmethod
    def validate_employee_data(fio: str, position: str, rate: float, norm_hours: int) -> Tuple[bool, Optional[str]]:
        """Валидация данных сотрудника.
        
        Returns:
            (is_valid, error_message)
        """
        if not fio or not fio.strip():
            return False, "ФИО не может быть пустым"
        
        if len(fio) > 255:
            return False, "ФИО слишком длинное (макс. 255 символов)"
        
        if not position or not position.strip():
            return False, "Должность не может быть пустой"
        
        if len(position) > 100:
            return False, "Должность слишком длинная (макс. 100 символов)"
        
        if rate < 0:
            return False, "Ставка не может быть отрицательной"
        
        if rate > 999.99:
            return False, "Ставка слишком велика (макс. 999.99)"
        
        if norm_hours < 0:
            return False, "Норма часов не может быть отрицательной"
        
        return True, None

    @staticmethod
    def validate_dates(start_date: date, end_date: date) -> Tuple[bool, Optional[str]]:
        """Валидация диапазона дат.
        
        Returns:
            (is_valid, error_message)
        """
        if not start_date:
            return False, "Дата начала не указана"
        
        if not end_date:
            return False, "Дата окончания не указана"
        
        if end_date < start_date:
            return False, "Дата окончания не может быть раньше даты начала"
        
        return True, None

    @staticmethod
    def validate_document_type(doc_type: str) -> Tuple[bool, Optional[str]]:
        """Валидация типа документа."""
        valid_types = ['Отпуск', 'Больничный', 'Командировка', 'Отгул']
        
        if not doc_type or doc_type not in valid_types:
            return False, f"Недопустимый тип документа. Допустимые: {', '.join(valid_types)}"
        
        return True, None

    @staticmethod
    def validate_hours(hours: float) -> Tuple[bool, Optional[str]]:
        """Валидация количества часов."""
        if hours < 0:
            return False, "Количество часов не может быть отрицательным"
        
        if hours > 24:
            return False, "Количество часов не может превышать 24"
        
        return True, None

    @staticmethod
    def validate_day_type(day_type: str) -> Tuple[bool, Optional[str]]:
        """Валидация типа дня."""
        valid_types = [
            'Рабочий день', 'Отпуск', 'Больничный', 
            'Командировка', 'Отгул', 'Неявка'
        ]
        
        if not day_type or day_type not in valid_types:
            return False, f"Недопустимый тип дня. Допустимые: {', '.join(valid_types)}"
        
        return True, None

    @staticmethod
    def validate_timesheet_status(status: str) -> Tuple[bool, Optional[str]]:
        """Валидация статуса табеля."""
        valid_statuses = ['В работе', 'Утверждён', 'Архивирован']
        
        if status not in valid_statuses:
            return False, f"Недопустимый статус. Допустимые: {', '.join(valid_statuses)}"
        
        return True, None

    @staticmethod
    def validate_login_credentials(username: str, password: str) -> Tuple[bool, Optional[str]]:
        """Валидация данных для входа."""
        if not username or not username.strip():
            return False, "Введите имя пользователя"
        
        if not password:
            return False, "Введите пароль"
        
        if len(username) > 100:
            return False, "Имя пользователя слишком длинное"
        
        return True, None

    @staticmethod
    def validate_password_change(old_password: str, new_password: str, confirm_password: str) -> Tuple[bool, Optional[str]]:
        """Валидация смены пароля."""
        if not old_password:
            return False, "Введите текущий пароль"
        
        if not new_password:
            return False, "Введите новый пароль"
        
        if len(new_password) < 6:
            return False, "Пароль должен быть не менее 6 символов"
        
        if new_password != confirm_password:
            return False, "Пароли не совпадают"
        
        return True, None
