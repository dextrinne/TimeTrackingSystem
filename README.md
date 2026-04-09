# ПС «Учёт рабочего времени сотрудников института»

---

## Описание проекта

Программная система для автоматизации процессов планирования, фиксации, согласования и контроля фактически отработанного времени сотрудниками ИММИ КубГУ.

### Назначение
- Автоматизация учёта рабочего времени
- Формирование электронного табеля
- Управление кадровыми документами (отпуска, больничные, командировки)
- Генерация отчётов и выгрузка в XLSX
- Разграничение прав доступа


---

## Структура проекта

```
TimeTrackingSystem/
├── main.py                     # Точка входа
├── config.py                   # Конфигурация (БД, настройки)
├── requirements.txt            # Зависимости
├── README.md                   # Документация
├── database/
│   ├── __init__.py
│   ├── db_manager.py           # Менеджер подключения к БД
│   ├── models.py               # Модели данных
│   └── init_db.sql             # SQL-скрипт инициализации
├── services/
│   ├── __init__.py
│   ├── employee_service.py     # Сервис сотрудников
│   ├── timesheet_service.py    # Сервис табелей
│   ├── document_service.py     # Сервис документов
│   └── report_service.py       # Сервис отчётов
├── ui/
│   ├── __init__.py
│   ├── login_window.py         # Окно авторизации
│   ├── main_window.py          # Главное окно
│   ├── employee_tab.py         # Вкладка сотрудников
│   ├── timesheet_tab.py        # Вкладка табелей
│   ├── document_tab.py         # Вкладка документов
│   └── report_tab.py           # Вкладка отчётов
└── utils/
    ├── __init__.py
    └── validators.py           # Валидация данных
```

---

## Установка и запуск

### 1. Требования
- Python 3.8+
- PostgreSQL 14+
- pip

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка базы данных

1. Убедитесь, что PostgreSQL запущен
2. Откройте pgAdmin4 или psql
3. Выполните скрипт инициализации:
   ```bash
   psql -U postgres -f database/init_db.sql
   ```
   Или вручную создайте БД `time_tracking` и выполните SQL-запросы из `database/init_db.sql`

4. Обновите настройки подключения в `config.py` (если необходимо):
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'port': 5432,
       'database': 'time_tracking',
       'user': 'postgres',
       'password': 'postgres'
   }
   ```

### 4. Запуск приложения
```bash
python main.py
```

