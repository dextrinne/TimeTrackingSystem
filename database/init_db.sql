-- ============================================================
-- Инициализация базы данных "Учёт рабочего времени сотрудников"
-- СУБД: PostgreSQL 14+
-- ЛР4: Лабораторная работа №4 — Разработка информационного обеспечения
-- ============================================================

-- Создание базы данных
CREATE DATABASE time_tracking;

-- Подключение к базе (выполнить отдельно)
-- \c time_tracking;

-- ============================================================
-- Таблица: employee (Сотрудники)
-- ============================================================
CREATE TABLE IF NOT EXISTS employee (
    id_employee SERIAL PRIMARY KEY,
    fio VARCHAR(255) NOT NULL,
    position VARCHAR(100),
    rate NUMERIC(5,2) CHECK (rate >= 0),
    norm_hours INT CHECK (norm_hours >= 0)
);

-- ============================================================
-- Таблица: timesheet (Табель)
-- ============================================================
CREATE TABLE IF NOT EXISTS timesheet (
    id_timesheet SERIAL PRIMARY KEY,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL CHECK (period_end >= period_start),
    status VARCHAR(50) DEFAULT 'В работе' CHECK (status IN ('В работе', 'Утверждён', 'Архивирован')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    archived_at TIMESTAMP
);

-- ============================================================
-- Таблица: timesheet_entry (Записи табеля)
-- ============================================================
CREATE TABLE IF NOT EXISTS timesheet_entry (
    id_timesheet_entry SERIAL PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employee(id_employee),
    timesheet_id INT NOT NULL REFERENCES timesheet(id_timesheet),
    date DATE NOT NULL,
    hours_worked NUMERIC(4,2) DEFAULT 0 CHECK (hours_worked >= 0),
    type VARCHAR(50) CHECK (type IN ('Рабочий день', 'Отпуск', 'Больничный', 'Командировка', 'Отгул', 'Неявка'))
);

-- ============================================================
-- Таблица: document (Документы)
-- ============================================================
CREATE TABLE IF NOT EXISTS document (
    id_document SERIAL PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employee(id_employee),
    type VARCHAR(50) NOT NULL CHECK (type IN ('Отпуск', 'Больничный', 'Командировка', 'Отгул')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL CHECK (end_date >= start_date)
);

-- ============================================================
-- Таблица: users (Пользователи системы)
-- Для реализации авторизации и разграничения прав (ЛР1-НФ3,НФ4)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id_user SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'Табельщик' CHECK (role = 'Табельщик'),
    employee_id INT REFERENCES employee(id_employee),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Таблица: activity_log (Журнал действий)
-- Для реализации логирования (ЛР2-Управляющие функции)
-- ============================================================
CREATE TABLE IF NOT EXISTS activity_log (
    id_log SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id_user),
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Тестовые данные
-- ============================================================

-- Пользователи (пароль: "tabel123", хеш SHA-256)
INSERT INTO users (username, password_hash, role) VALUES
('tabel', '763bd343720eb5fdf55339f759e5a2411a82c770f0221e9ee4f7de10b59885f8', 'Табельщик');

-- Сотрудники
INSERT INTO employee (fio, position, rate, norm_hours) VALUES
('Иванов Иван Иванович', 'Научный сотрудник', 1.0, 40),
('Петрова Мария Сергеевна', 'Аспирант', 0.5, 20),
('Сидоров Алексей Николаевич', 'Профессор', 1.0, 40),
('Козлова Елена Викторовна', 'Доцент', 0.75, 30),
('Морозов Дмитрий Александрович', 'Студент', 0.25, 10);

-- Документы (отпуска, больничные)
INSERT INTO document (employee_id, type, start_date, end_date) VALUES
(1, 'Отпуск', '2026-03-01', '2026-03-14'),
(2, 'Больничный', '2026-03-10', '2026-03-15'),
(3, 'Командировка', '2026-03-20', '2026-03-25');

-- Табель за март 2026
INSERT INTO timesheet (period_start, period_end, status) VALUES
('2026-03-01', '2026-03-31', 'В работе');

-- Записи табеля (пример для первого сотрудника)
INSERT INTO timesheet_entry (employee_id, timesheet_id, date, hours_worked, type) VALUES
(1, 1, '2026-03-02', 8, 'Рабочий день'),
(1, 1, '2026-03-03', 8, 'Рабочий день'),
(1, 1, '2026-03-04', 8, 'Рабочий день'),
(1, 1, '2026-03-05', 8, 'Рабочий день'),
(1, 1, '2026-03-06', 8, 'Рабочий день');
