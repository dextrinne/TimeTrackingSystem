@echo off
chcp 65001 >nul
echo ============================================================
echo Сборка ПС "Учёт рабочего времени сотрудников ИММИ КубГУ"
echo PyQt5 + PyInstaller
echo ============================================================
echo.

echo [1/2] Проверка зависимостей...
pip install PyQt5 psycopg2-binary openpyxl pyinstaller >nul 2>&1
echo [OK] Зависимости проверены
echo.

echo [2/2] Сборка .exe (PyInstaller)...
echo Закрытие запущенных процессов...
taskkill /F /IM TimeTrackingSystem.exe 2>nul
timeout /t 2 /nobreak >nul

rmdir /s /q build dist 2>nul

python -m PyInstaller --clean --onefile --windowed ^
    --name="TimeTrackingSystem" ^
    --add-data "config.py;." ^
    --add-data "database;database" ^
    --add-data "services;services" ^
    --add-data "ui;ui" ^
    --add-data "utils;utils" ^
    main.py

if %errorlevel% neq 0 (
    echo [ERROR] Ошибка сборки
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [OK] Сборка завершена!
echo ============================================================
echo.
echo Готовый файл: dist\TimeTrackingSystem.exe
echo.
echo Для запуска дважды кликните по файлу .exe
echo ============================================================
pause
