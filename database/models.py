"""
Модели данных ПС «Учёт рабочего времени сотрудников».
ЛР4: Модели соответствуют физической модели данных из ER-диаграммы.
"""

from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class TimesheetStatus(Enum):
    """Статусы табеля (ЛР2-Управляющие функции)."""
    IN_PROGRESS = "В работе"
    APPROVED = "Утверждён"
    ARCHIVED = "Архивирован"


class DayType(Enum):
    """Типы дней в табеле."""
    WORKDAY = "Рабочий день"
    VACATION = "Отпуск"
    SICK_LEAVE = "Больничный"
    BUSINESS_TRIP = "Командировка"
    DAY_OFF = "Отгул"
    ABSENT = "Неявка"


class UserRole(Enum):
    """Роль пользователя (ЛР1-НФ3). Единственная роль — Табельщик."""
    TABELSHCHIK = "Табельщик"


@dataclass
class Employee:
    """Модель сотрудника."""
    id_employee: Optional[int] = None
    fio: str = ""
    position: str = ""
    rate: float = 1.0
    norm_hours: int = 40

    def to_dict(self):
        return {
            'id_employee': self.id_employee,
            'fio': self.fio,
            'position': self.position,
            'rate': self.rate,
            'norm_hours': self.norm_hours
        }

    @staticmethod
    def from_row(row):
        """Создание объекта из строки БД."""
        if row is None:
            return None
        return Employee(
            id_employee=row[0],
            fio=row[1],
            position=row[2],
            rate=float(row[3]) if row[3] is not None else 0.0,
            norm_hours=row[4] if row[4] is not None else 0
        )


@dataclass
class Timesheet:
    """Модель табеля учёта рабочего времени."""
    id_timesheet: Optional[int] = None
    period_start: date = field(default_factory=date.today)
    period_end: date = field(default_factory=date.today)
    status: str = TimesheetStatus.IN_PROGRESS.value
    created_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None

    def to_dict(self):
        return {
            'id_timesheet': self.id_timesheet,
            'period_start': self.period_start,
            'period_end': self.period_end,
            'status': self.status,
            'created_at': self.created_at,
            'approved_at': self.approved_at,
            'archived_at': self.archived_at
        }

    @staticmethod
    def from_row(row):
        """Создание объекта из строки БД."""
        if row is None:
            return None
        return Timesheet(
            id_timesheet=row[0],
            period_start=row[1],
            period_end=row[2],
            status=row[3],
            created_at=row[4],
            approved_at=row[5],
            archived_at=row[6]
        )


@dataclass
class TimesheetEntry:
    """Модель записи табеля (один день одного сотрудника)."""
    id_timesheet_entry: Optional[int] = None
    employee_id: int = 0
    timesheet_id: int = 0
    date: date = field(default_factory=date.today)
    hours_worked: float = 0.0
    type: str = DayType.WORKDAY.value

    def to_dict(self):
        return {
            'id_timesheet_entry': self.id_timesheet_entry,
            'employee_id': self.employee_id,
            'timesheet_id': self.timesheet_id,
            'date': self.date,
            'hours_worked': self.hours_worked,
            'type': self.type
        }

    @staticmethod
    def from_row(row):
        """Создание объекта из строки БД."""
        if row is None:
            return None
        return TimesheetEntry(
            id_timesheet_entry=row[0],
            employee_id=row[1],
            timesheet_id=row[2],
            date=row[3],
            hours_worked=float(row[4]) if row[4] is not None else 0.0,
            type=row[5]
        )


@dataclass
class Document:
    """Модель документа (отпуск, больничный, командировка)."""
    id_document: Optional[int] = None
    employee_id: int = 0
    type: str = ""
    start_date: date = field(default_factory=date.today)
    end_date: date = field(default_factory=date.today)

    def to_dict(self):
        return {
            'id_document': self.id_document,
            'employee_id': self.employee_id,
            'type': self.type,
            'start_date': self.start_date,
            'end_date': self.end_date
        }

    @staticmethod
    def from_row(row):
        """Создание объекта из строки БД."""
        if row is None:
            return None
        return Document(
            id_document=row[0],
            employee_id=row[1],
            type=row[2],
            start_date=row[3],
            end_date=row[4]
        )


@dataclass
class User:
    """Модель пользователя системы (ЛР1-НФ3,НФ4)."""
    id_user: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    role: str = UserRole.TABELSHCHIK.value
    employee_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def from_row(row):
        """Создание объекта из строки БД."""
        if row is None:
            return None
        return User(
            id_user=row[0],
            username=row[1],
            password_hash=row[2],
            role=row[3],
            employee_id=row[4],
            created_at=row[5]
        )


@dataclass
class ActivityLog:
    """Модель журнала действий (ЛР2-Управляющие функции)."""
    id_log: Optional[int] = None
    user_id: Optional[int] = None
    action: str = ""
    entity_type: str = ""
    entity_id: Optional[int] = None
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def from_row(row):
        """Создание объекта из строки БД."""
        if row is None:
            return None
        return ActivityLog(
            id_log=row[0],
            user_id=row[1],
            action=row[2],
            entity_type=row[3],
            entity_id=row[4],
            description=row[5],
            created_at=row[6]
        )


@dataclass
class Report:
    """Модель отчёта (ЛР2-Абстракция «Отчёт»).

    Формируется на основе данных табеля и содержит сводную
    информацию по каждому сотруднику за отчётный период.
    """
    id_report: Optional[int] = None
    timesheet_id: int = 0
    period_start: date = field(default_factory=date.today)
    period_end: date = field(default_factory=date.today)
    generated_at: datetime = field(default_factory=datetime.now)
    data: list = field(default_factory=list)  # Список словарей с данными по сотрудникам

    def to_dict(self):
        return {
            'id_report': self.id_report,
            'timesheet_id': self.timesheet_id,
            'period_start': self.period_start,
            'period_end': self.period_end,
            'generated_at': self.generated_at,
            'data': self.data
        }


@dataclass
class Archive:
    """Модель архива (ЛР2-Абстракция «Архив»).

    Контейнер для хранения и поиска табелей за прошлые периоды.
    Обеспечивает долговременное хранение и извлечение данных.
    """
    id_archive: Optional[int] = None
    timesheet_id: int = 0
    archived_at: datetime = field(default_factory=datetime.now)
    period_start: date = field(default_factory=date.today)
    period_end: date = field(default_factory=date.today)
    comment: str = ""

    @staticmethod
    def from_row(row):
        """Создание объекта из строки БД."""
        if row is None:
            return None
        return Archive(
            id_archive=row[0],
            timesheet_id=row[1],
            archived_at=row[2],
            period_start=row[3],
            period_end=row[4],
            comment=row[5] if len(row) > 5 else ""
        )
