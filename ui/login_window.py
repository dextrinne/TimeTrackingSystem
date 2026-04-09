"""
Окно авторизации на tkinter.
ЛР1-НФ3,НФ4: Разграничение прав доступа, авторизация по логину/паролю.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager


class LoginWindow(tk.Toplevel):
    """Окно входа в систему."""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.current_user = None
        self.result = False
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        self.title('Вход в систему — Учёт рабочего времени')
        self.geometry('400x300')
        self.resizable(False, False)
        self.transient()
        self.grab_set()

        # Центрирование
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 300) // 2
        self.geometry(f'400x300+{x}+{y}')

        # Заголовок
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(30, 10))

        title_label = ttk.Label(
            title_frame, 
            text='Учёт рабочего времени',
            font=('Arial', 16, 'bold')
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame, 
            text='ИММИ КубГУ',
            font=('Arial', 10),
            foreground='gray'
        )
        subtitle_label.pack()

        # Форма входа
        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.X, padx=40, pady=20)

        # Логин
        ttk.Label(form_frame, text='Логин:').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.login_var = tk.StringVar()
        self.login_entry = ttk.Entry(form_frame, textvariable=self.login_var, width=30)
        self.login_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        self.login_entry.focus_set()

        # Пароль
        ttk.Label(form_frame, text='Пароль:').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show='*', width=30)
        self.password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        self.password_entry.bind('<Return>', lambda e: self.login())

        # Кнопки
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=40, pady=10)

        login_btn = ttk.Button(button_frame, text='Войти', command=self.login)
        login_btn.pack(side=tk.LEFT, padx=5, expand=True)

        cancel_btn = ttk.Button(button_frame, text='Отмена', command=self.cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5, expand=True)

    def login(self):
        """Обработка входа."""
        username = self.login_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            messagebox.warning(self, 'Ошибка', 'Введите логин и пароль')
            return

        try:
            row = self.db.execute_query(
                """SELECT id_user, username, password_hash, role, employee_id 
                   FROM users WHERE username = %s""",
                (username,),
                fetchone=True
            )

            if row:
                user_id, db_username, stored_password, role, employee_id = row
                
                # Простая проверка (для демо — сравнение с plaintext)
                if password == stored_password:
                    self.current_user = {
                        'id_user': user_id,
                        'username': db_username,
                        'role': role,
                        'employee_id': employee_id
                    }
                    self.result = True
                    self.destroy()
                else:
                    messagebox.warning(self, 'Ошибка', 'Неверный логин или пароль')
            else:
                messagebox.warning(self, 'Ошибка', 'Неверный логин или пароль')

        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка входа: {str(e)}')

    def cancel(self):
        """Отмена входа."""
        self.result = False
        self.destroy()

    def get_user(self):
        """Получить данные текущего пользователя."""
        return self.current_user
