# Документация по тестированию ПС «Учёт рабочего времени сотрудников»

## Обзор

Проект содержит **комплексную систему тестирования**, покрывающую все компоненты приложения:
- Модели данных
- Сервисы (бизнес-логика)
- Валидаторы
- UI компоненты (диалоги, вкладки, главное окно)
- Интеграционные сценарии
- Обработку ошибок и пограничные случаи

## Структура тестов

```
tests/
├── __init__.py                           # Инициализация пакета
├── conftest.py                           # Фикстуры и общая инфраструктура (psycopg2 моки)
├── test_models.py                        # Оригинальные тесты моделей
├── test_models_comprehensive.py          # Комплексные тесты моделей (8 моделей + enums)
├── test_services.py                      # Интеграционные тесты сервисов (psycopg2 моки)
├── test_services_comprehensive.py        # Комплексные тесты всех сервисов
├── test_validators.py                    # Оригинальные тесты валидаторов
├── test_validators_comprehensive.py      # Комплексные тесты валидаторов
├── test_db_manager.py                    # Тесты DatabaseManager (psycopg2 моки)
├── test_login_dialog.py                  # Тесты LoginDialog
├── test_dialogs.py                       # Тесты EmployeeDialog, TimesheetDialog, DocumentDialog
├── test_tabs.py                          # Тесты всех вкладок
├── test_main_window.py                   # Тесты MainWindow
├── test_integration.py                   # Интеграционные тесты полного цикла
└── test_errors_and_edge_cases.py         # Тесты обработки ошибок и пограничных случаев
```

## Запуск тестов

### Запуск всех тестов

```bash
# Из корня проекта TimeTrackingSystem
python run_all_tests.py

# С подробным выводом
python run_all_tests.py -v

# Тихий режим
python run_all_tests.py -q
```

### Запуск конкретного модуля

```bash
# Только тесты моделей
python -m unittest tests.test_models_comprehensive

# Только тесты сервисов
python -m unittest tests.test_services_comprehensive

# Только интеграционные тесты
python -m unittest tests.test_integration

# Тесты валидаторов
python -m unittest tests.test_validators_comprehensive
```

### Запуск конкретного теста

```bash
# Конкретный тест из модуля
python -m unittest tests.test_models_comprehensive.TestEmployeeModel.test_to_dict

# Все тесты с словом "validation"
python -m unittest discover tests -p "*validation*"
```

## Описание тестовых модулей

### 1. `test_models_comprehensive.py` (8 моделей + enums)

**Классы тестов:**
- `TestEmployeeModel` - модель сотрудника (10 тестов)
- `TestTimesheetModel` - модель табеля (7 тестов)
- `TestTimesheetEntryModel` - модель записи табеля (8 тестов)
- `TestDocumentModel` - модель документа (9 тестов)
- `TestUserModel` - модель пользователя (5 тестов)
- `TestActivityLogModel` - модель журнала действий (5 тестов)
- `TestReportModel` - модель отчёта (5 тестов)
- `TestArchiveModel` - модель архива (6 тестов)
- `TestEnums` - перечисления (4 теста)

**Что покрывает:**
- Значения по умолчанию
- Сериализация/десериализация (`to_dict`, `from_row`)
- Пользовательские значения
- Пограничные случаи (мин/макс, None, пустые строки, юникод)
- Enum классы (TimesheetStatus, DayType, UserRole)

### 2. `test_services_comprehensive.py` (4 сервиса)

**Классы тестов:**
- `TestEmployeeServiceComprehensive` - CRUD сотрудников (11 тестов)
- `TestTimesheetServiceComprehensive` - CRUD табелей (12 тестов)
- `TestDocumentServiceComprehensive` - CRUD документов (9 тестов)
- `TestReportServiceComprehensive` - отчёты и экспорт (5 тестов)

**Что покрывает:**
- Создание, чтение, обновление, удаление
- Поиск и фильтрация
- Подсчёт итогов
- Генерация структуры табеля
- Формирование отчётов
- Экспорт в XLSX

### 3. `test_validators_comprehensive.py` (полное покрытие)

**Классы тестов:**
- `TestEmployeeValidationComprehensive` - валидация сотрудников (15 тестов)
- `TestDateValidationComprehensive` - валидация дат (10 тестов)
- `TestDocumentTypeValidationComprehensive` - типы документов (10 тестов)
- `TestHoursValidationComprehensive` - валидация часов (9 тестов)
- `TestDayTypeValidationComprehensive` - типы дней (7 тестов)
- `TestTimesheetStatusValidationComprehensive` - статусы табеля (7 тестов)
- `TestLoginValidationComprehensive` - авторизация (11 тестов)
- `TestPasswordChangeValidationComprehensive` - смена пароля (10 тестов)

**Что покрывает:**
- Все корректные данные
- Все некорректные данные
- Пограничные значения (мин/макс, ровно лимит, на 1 больше/меньше)
- Пустые значения, None, пробелы
- Юникод и спецсимволы
- Регистрозависимость

### 4. `test_db_manager.py` (DatabaseManager)

**Классы тестов:**
- `TestDatabaseManagerMock` - тесты с моками psycopg2 (12 тестов)
- `TestDatabaseManagerTransaction` - тесты транзакций (2 теста)
- `TestDatabaseManagerBackup` - тесты резервного копирования (3 теста)
- `TestDatabaseManagerInit` - тесты инициализации БД (2 теста)
- `TestDatabaseManagerEdgeCases` - пограничные случаи (5 тестов)

**Что покрывает:**
- Подключение к БД
- Выполнение запросов (INSERT, UPDATE, DELETE, SELECT)
- Транзакции (commit/rollback)
- Параметризированные запросы (защита от SQL-инъекций)
- Множественная вставка
- Обработка ошибок
- Большие объемы данных (1000 записей)

### 5. `test_login_dialog.py` (LoginDialog)

**Классы тестов:**
- `TestLoginDialogUI` - UI тесты (18 тестов)
- `TestLoginDialogDatabaseError` - ошибки БД (1 тест)

**Что покрывает:**
- Начальное состояние диалога
- Скрытость пароля по умолчанию
- Переключение видимости пароля
- Валидация пустых полей
- Успешный/неуспешный вход
- Сохранение/очистка учётных данных
- Загрузка сохранённых данных
- Ошибки БД

### 6. `test_dialogs.py` (EmployeeDialog, TimesheetDialog, DocumentDialog)

**Классы тестов:**
- `TestEmployeeDialog` - диалог сотрудника (11 тестов)
- `TestTimesheetDialog` - диалог табеля (6 тестов)
- `TestDocumentDialog` - диалог документа (8 тестов)
- `TestDialogEdgeCases` - пограничные случаи (4 теста)

**Что покрывает:**
- Заголовки диалогов
- Существование полей и кнопок
- Заполнение форм
- Валидация данных
- Сохранение/обновление
- Пограничные значения

### 7. `test_tabs.py` (вкладки главного окна)

**Классы тестов:**
- `TestEmployeesTab` - вкладка сотрудников (7 тестов)
- `TestTimesheetsTab` - вкладка табелей (9 тестов)
- `TestDocumentsTab` - вкладка документов (8 тестов)
- `TestReportsTab` - вкладка отчётов (7 тестов)
- `TestTabsIntegration` - интеграция (1 тест)

**Что покрывает:**
- Заголовки вкладок
- Существование элементов UI
- Загрузка данных
- Поиск и фильтрация
- Количество колонок таблиц

### 8. `test_main_window.py` (MainWindow)

**Классы тестов:**
- `TestMainWindow` - главное окно (14 тестов)
- `TestMainWindowDatabaseBackup` - резервное копирование (2 теста)
- `TestMainWindowPermissions` - права доступа (1 тест)

**Что покрывает:**
- Заголовок окна
- Вкладки (наличие, названия)
- Менюбар (Файл, Справка)
- Статусбар (информация о пользователе)
- Действия меню (Backup, Выход, О программе)
- Закрытие окна с подтверждением

### 9. `test_integration.py` (интеграционные тесты)

**Классы тестов:**
- `TestFullWorkflow` - полный цикл (5 тестов)
- `TestMultipleTimesheetsWorkflow` - несколько табелей (1 тест)
- `TestStatusTransitionWorkflow` - переходы статусов (3 теста)

**Что покрывает:**
- **Полный рабочий процесс:**
  1. Создание сотрудников
  2. Создание табеля
  3. Добавление записей
  4. Создание документов
  5. Подсчёт итогов
  6. Формирование отчёта
  7. Экспорт в XLSX
  8. Изменение статуса
- Поиск сотрудников
- Проверка пересечения документов
- Автогенерация табеля
- Валидация данных
- Несколько табелей для одного сотрудника
- Переходы статусов (В работе → Утверждён → Архивирован)

### 10. `test_errors_and_edge_cases.py` (обработка ошибок)

**Классы тестов:**
- `TestDatabaseErrors` - ошибки БД (8 тестов)
- `TestServiceErrors` - ошибки сервисов (4 теста)
- `TestModelEdgeCases` - пограничные случаи моделей (8 тестов)
- `TestValidatorEdgeCases` - пограничные случаи валидаторов (12 тестов)
- `TestDateEdgeCases` - пограничные случаи дат (6 тестов)
- `TestUnicodeAndSpecialCharacters` - юникод и спецсимволы (6 тестов)

**Что покрывает:**
- Нарушения ограничений БД (NOT NULL, FK)
- Неверный SQL синтаксис
- Несуществующие таблицы/колонки
- Откат транзакций
- Производительность (10000 записей)
- Очень длинные строки
- Даты в прошлом/будущем/високосных годах
- Отрицательные/очень большие числа
- SQL-инъекции
- Юникод (кириллица, эмодзи, смешанные)
- Специальные XML символы

## Статистика тестов

| Категория | Количество тестов |
|-----------|------------------|
| Модели данных | ~65 |
| Сервисы | ~37 |
| Валидаторы | ~79 |
| DatabaseManager | ~24 |
| UI диалоги | ~48 |
| UI вкладки | ~41 |
| MainWindow | ~17 |
| Интеграционные | ~9 |
| Ошибки и edge cases | ~44 |
| **ИТОГО** | **~364** |

## Фикстуры

В `conftest.py` определены:
- `project_root` - корень проекта
- `mock_db` - мок DatabaseManager (psycopg2)
- `sample_employee_data` - пример сотрудника
- `sample_timesheet_data` - пример табеля
- `sample_document_data` - пример документа
- `sample_user_data` - пример пользователя
- `sample_timesheet_entry_data` - пример записи табеля

## MockDBManager

Для тестов сервисов используются **моки psycopg2** (unittest.mock.Mock), которые полностью эмулируют работу с PostgreSQL без реальной базы данных:
- `execute_query` - возвращает заранее определённые данные
- `execute_many` - отслеживает вызовы множественной вставки
- Поддержка `fetch`, `fetchone`

## Требования

Все зависимости указаны в `requirements.txt`:
```
PyQt5==5.15.11
psycopg2-binary==2.9.11
openpyxl==3.1.5
pyinstaller==6.16.0
```

Для запуска UI тестов требуется PyQt5.

## Непрерывная интеграция

Рекомендуется запускать все тесты перед каждым коммитом:
```bash
python run_all_tests.py
```

## Покрытие кода

Для проверки покрытия кода можно использовать `coverage`:
```bash
pip install coverage
coverage run run_all_tests.py
coverage report -m
coverage html
```

## Рекомендации

1. **Запускать все тесты** перед каждым коммитом
2. **Добавлять новые тесты** при добавлении функционала
3. **Использовать моки** для изоляции компонентов
4. **Писать интеграционные тесты** для критических сценариев
5. **Тестировать ошибки** и пограничные случаи

## Архитектура тестов

```
┌─────────────────────────────────────────┐
│          run_all_tests.py               │
│       (Главный запускальщик)            │
└───────────────┬─────────────────────────┘
                │
    ┌───────────┼───────────────┐
    │           │               │
┌───▼───┐ ┌────▼────┐ ┌───────▼───────┐
│Models │ │Services │ │  Validators   │
└───────┘ └─────────┘ └───────────────┘
    │           │               │
    └───────────┼───────────────┘
                │
    ┌───────────┼───────────────┐
    │           │               │
┌───▼───┐ ┌────▼────┐ ┌───────▼───────┐
│  UI   │ │Integration│ │  Edge Cases │
│Dialogs│ │  Tests    │ │   & Errors  │
└───────┘ └───────────┘ └───────────────┘
```

## Контакты

По вопросам тестирования обращайтесь к разработчикам проекта.
