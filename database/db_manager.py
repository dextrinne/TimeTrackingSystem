"""
Менеджер подключения к базе данных PostgreSQL.
Обеспечивает подключение, выполнение запросов и управление транзакциями.
ЛР1-НФ1: Надёжность — восстановление после сбоев.
"""

import psycopg2
from psycopg2 import Error, pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG


class DatabaseManager:
    """Менеджер подключения к PostgreSQL."""

    def __init__(self, config=None):
        self.config = config or DB_CONFIG
        self.connection_pool = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Инициализация пула подключений."""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **self.config
            )
            print(f"[OK] Подключено к PostgreSQL: {self.config['database']}@{self.config['host']}")
        except Error as e:
            print(f"[ERROR] Ошибка подключения к PostgreSQL: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Получение подключения из пула (контекстный менеджер)."""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
            conn.commit()
        except Error as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] Ошибка выполнения запроса: {e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    @contextmanager
    def get_cursor(self):
        """Получение курсора для выполнения запросов."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()

    def execute_query(self, query, params=None, fetch=False, fetchone=False):
        """Выполнение запроса к БД.
        
        Args:
            query: SQL-запрос
            params: Параметры запроса
            fetch: Получить все результаты
            fetchone: Получить один результат
        
        Returns:
            Результаты запроса или None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            elif fetchone:
                return cursor.fetchone()
            return None

    def execute_many(self, query, params_list):
        """Выполнение множественной вставки/обновления."""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)

    def backup_database(self, backup_path):
        """Создание резервной копии БД (ЛР1-НФ1, ЛР3-Т-1)."""
        try:
            import subprocess
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config['password']
            
            cmd = [
                'pg_dump',
                '-h', self.config['host'],
                '-p', str(self.config['port']),
                '-U', self.config['user'],
                '-d', self.config['database'],
                '-f', backup_path
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[OK] Резервная копия создана: {backup_path}")
                return True
            else:
                print(f"[ERROR] Ошибка создания backup: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Ошибка backup: {e}")
            return False

    def init_database(self, sql_file_path):
        """Инициализация БД из SQL файла."""
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Подключаемся к postgres для создания БД
            admin_config = {**self.config}
            admin_conn = psycopg2.connect(**admin_config)
            admin_conn.autocommit = True
            cursor = admin_conn.cursor()
            
            # Проверяем существует ли БД
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.config['database']}'")
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f"CREATE DATABASE {self.config['database']}")
                print(f"[OK] База данных '{self.config['database']}' создана")
            else:
                print(f"[OK] База данных '{self.config['database']}' уже существует")
            
            cursor.close()
            admin_conn.close()
            
            # Выполняем SQL скрипт
            conn = psycopg2.connect(**self.config)
            cursor = conn.cursor()
            cursor.execute(sql_script)
            conn.commit()
            cursor.close()
            conn.close()
            
            print("[OK] SQL скрипт выполнен успешно")
            return True

        except Exception as e:
            print(f"[ERROR] Ошибка инициализации БД: {e}")
            return False

    def close_all(self):
        """Закрытие всех подключений."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("[OK] Все подключения к PostgreSQL закрыты")
