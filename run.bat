@echo off
REM Скрипт для запуска приложения "Система управления табелями"
REM Script to run Time Tracking System application

setlocal enabledelayedexpansion

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ОШИБКА: Python не установлен или не добавлен в PATH
    echo ERROR: Python is not installed or not added to PATH
    echo.
    echo Пожалуйста, установите Python с сайта: https://www.python.org/
    echo Please install Python from: https://www.python.org/
    pause
    exit /b 1
)

REM Проверка наличия необходимых библиотек
echo Проверка зависимостей...
python -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Установка необходимых библиотек...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ОШИБКА при установке зависимостей
        pause
        exit /b 1
    )
)

REM Запуск приложения
echo.
echo Запуск приложения "Система управления табелями"...
echo.
python app.py

if errorlevel 1 (
    echo.
    echo ОШИБКА при запуске приложения
    pause
    exit /b 1
)

endlocal
