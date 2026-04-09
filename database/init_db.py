"""
Скрипт инициализации базы данных PostgreSQL.
Создаёт БД и выполняет SQL из init_db.sql
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from config import DB_CONFIG

def init_database():
    """Создание и инициализация базы данных."""
    print("=== Инициализация базы данных PostgreSQL ===\n")
    
    try:
        # Подключаемся к серверу PostgreSQL (к БД postgres)
        admin_config = {**DB_CONFIG, 'database': 'postgres'}
        print(f"Подключение к PostgreSQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        conn = psycopg2.connect(**admin_config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Проверяем существует ли БД
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_CONFIG['database']}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Создание базы данных '{DB_CONFIG['database']}'...")
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print("[OK] База данных создана")
        else:
            print(f"[OK] База данных '{DB_CONFIG['database']}' уже существует")
        
        cursor.close()
        conn.close()
        
        # Подключаемся к нашей БД и выполняем скрипт
        print(f"\nПодключение к базе '{DB_CONFIG['database']}'...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Читаем SQL скрипт
        import os
        sql_file = os.path.join(os.path.dirname(__file__), 'init_db.sql')
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Убираем CREATE DATABASE из скрипта (мы уже создали)
        lines = sql_content.split('\n')
        filtered_lines = []
        skip_next = False
        for line in lines:
            if 'CREATE DATABASE' in line:
                skip_next = True
                continue
            if skip_next and ('--' in line or line.strip() == ''):
                continue
            if '-- Подключение к базе' in line:
                continue
            skip_next = False
            filtered_lines.append(line)
        
        filtered_sql = '\n'.join(filtered_lines)
        
        # Выполняем SQL
        print("Выполнение SQL скрипта...")
        cursor.execute(filtered_sql)
        conn.commit()
        cursor.close()
        conn.close()
        
        print("[OK] SQL скрипт выполнен успешно\n")
        print("=== База данных готова к работе! ===\n")
        print("Данные для входа:")
        print("  Логин: admin, Пароль: admin123 (Администратор)")
        print("  Логин: head, Пароль: head123 (Руководитель)")
        print("  Логин: tabel, Пароль: tabel123 (Табельщик)")
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n[ERROR] Ошибка PostgreSQL: {e}")
        print("\nУбедитесь что:")
        print("  1. PostgreSQL запущен")
        print("  2. Пароль в config.py правильный")
        print("  3. Пользователь имеет права на создание БД")
        return False
    except Exception as e:
        print(f"\n[ERROR] Ошибка: {e}")
        return False

if __name__ == '__main__':
    init_database()
