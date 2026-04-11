"""
Комплексные тесты UI компонентов: EmployeeDialog, TimesheetDialog, DocumentDialog.
Покрывает: валидацию форм, CRUD операции UI, обработку ошибок.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest


def get_qapp():
    """Получить или создать QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


class TestEmployeeDialog(unittest.TestCase):
    """Тесты EmployeeDialog."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        """Настройка: создание диалога."""
        from ui.dialogs.employee_dialog import EmployeeDialog
        
        self.mock_db = Mock()
        self.dialog = EmployeeDialog(self.mock_db)

    def tearDown(self):
        self.dialog.close()
        self.dialog.deleteLater()

    def test_dialog_title_add_mode(self):
        """Заголовок в режиме добавления."""
        self.assertIn('Добавление', self.dialog.windowTitle())

    def test_dialog_title_edit_mode(self):
        """Заголовок в режиме редактирования."""
        from database.models import Employee
        
        emp = Employee(id_employee=1, fio='Иванов И.И.', position='Инженер', rate=1.0, norm_hours=40)
        dialog = EmployeeDialog(self.mock_db, employee=emp)
        
        self.assertIn('Редактирование', dialog.windowTitle())
        dialog.close()
        dialog.deleteLater()

    def test_form_fields_population(self):
        """Заполнение полей формы."""
        self.assertIsNotNone(self.dialog.fio_edit)
        self.assertIsNotNone(self.dialog.position_edit)
        self.assertIsNotNone(self.dialog.rate_spinbox)
        self.assertIsNotNone(self.dialog.norm_hours_spinbox)

    def test_default_values(self):
        """Значения по умолчанию."""
        self.assertEqual(self.dialog.fio_edit.text(), '')
        self.assertEqual(self.dialog.position_edit.text(), '')
        self.assertEqual(self.dialog.rate_spinbox.value(), 1.0)
        self.assertEqual(self.dialog.norm_hours_spinbox.value(), 40)

    def test_populate_existing_employee(self):
        """Заполнение формы данными существующего сотрудника."""
        from database.models import Employee
        
        emp = Employee(id_employee=1, fio='Петров П.П.', position='Научный сотрудник', rate=0.5, norm_hours=20)
        dialog = EmployeeDialog(self.mock_db, employee=emp)
        
        self.assertEqual(dialog.fio_edit.text(), 'Петров П.П.')
        self.assertEqual(dialog.position_edit.text(), 'Научный сотрудник')
        self.assertEqual(dialog.rate_spinbox.value(), 0.5)
        self.assertEqual(dialog.norm_hours_spinbox.value(), 20)
        
        dialog.close()
        dialog.deleteLater()

    def test_save_new_employee(self):
        """Сохранение нового сотрудника."""
        self.dialog.fio_edit.setText('Новый Сотрудник')
        self.dialog.position_edit.setText('Инженер')
        self.dialog.rate_spinbox.setValue(1.0)
        self.dialog.norm_hours_spinbox.setValue(40)
        
        self.dialog.save()
        
        # Проверяем что был вызван INSERT
        self.mock_db.execute_query.assert_called_once()
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('INSERT', call_args[0])

    def test_update_existing_employee(self):
        """Обновление существующего сотрудника."""
        from database.models import Employee
        
        emp = Employee(id_employee=1, fio='Старый', position='Должность', rate=1.0, norm_hours=40)
        dialog = EmployeeDialog(self.mock_db, employee=emp)
        
        dialog.fio_edit.setText('Обновленный')
        dialog.save()
        
        # Проверяем что был вызван UPDATE
        self.mock_db.execute_query.assert_called_once()
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('UPDATE', call_args[0])
        
        dialog.close()
        dialog.deleteLater()

    def test_validation_empty_fio(self):
        """Валидация: пустое ФИО."""
        from PyQt5.QtWidgets import QMessageBox
        
        self.dialog.fio_edit.setText('')
        self.dialog.position_edit.setText('Должность')
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.dialog.save()
            mock_warning.assert_called_once()

    def test_validation_empty_position(self):
        """Валидация: пустая должность."""
        from PyQt5.QtWidgets import QMessageBox
        
        self.dialog.fio_edit.setText('ФИО')
        self.dialog.position_edit.setText('')
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.dialog.save()
            mock_warning.assert_called_once()


class TestTimesheetDialog(unittest.TestCase):
    """Тесты TimesheetDialog."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        from ui.dialogs.timesheet_dialog import TimesheetDialog
        self.mock_db = Mock()
        self.dialog = TimesheetDialog(self.mock_db)

    def tearDown(self):
        self.dialog.close()
        self.dialog.deleteLater()

    def test_dialog_title(self):
        """Заголовок диалога."""
        self.assertIn('Создание', self.dialog.windowTitle())

    def test_date_fields_exist(self):
        """Существование полей дат."""
        self.assertIsNotNone(self.dialog.start_date_edit)
        self.assertIsNotNone(self.dialog.end_date_edit)

    def test_default_dates(self):
        """Даты по умолчанию (предыдущий месяц)."""
        # Проверяем что даты установлены
        start_date = self.dialog.start_date_edit.date().toPyDate()
        end_date = self.dialog.end_date_edit.date().toPyDate()
        
        # Дата окончания >= даты начала
        self.assertGreaterEqual(end_date, start_date)

    def test_save_creates_timesheet(self):
        """Сохранение создает табель."""
        self.dialog.save()
        
        # Проверяем вызов к БД
        self.mock_db.execute_query.assert_called_once()
        call_args = self.mock_db.execute_query.call_args[0]
        self.assertIn('INSERT', call_args[0])
        self.assertIn('timesheet', call_args[0])

    def test_validation_end_before_start(self):
        """Валидация: дата окончания раньше начала."""
        from PyQt5.QtWidgets import QMessageBox
        from PyQt5.QtCore import QDate
        
        self.dialog.start_date_edit.setDate(QDate(2026, 3, 31))
        self.dialog.end_date_edit.setDate(QDate(2026, 3, 1))
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.dialog.save()
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            self.assertIn('окончан', args[1].lower())


class TestDocumentDialog(unittest.TestCase):
    """Тесты DocumentDialog."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def setUp(self):
        from ui.dialogs.document_dialog import DocumentDialog
        self.mock_db = Mock()
        
        # Мок для получения списка сотрудников
        self.mock_db.execute_query.return_value = [
            (1, 'Иванов И.И.'),
            (2, 'Петров П.П.')
        ]
        
        self.dialog = DocumentDialog(self.mock_db)

    def tearDown(self):
        self.dialog.close()
        self.dialog.deleteLater()

    def test_dialog_title_add_mode(self):
        """Заголовок в режиме добавления."""
        self.assertIn('Добавление', self.dialog.windowTitle())

    def test_employee_combo_box_exists(self):
        """Существование comboBox сотрудников."""
        self.assertIsNotNone(self.dialog.employee_combo)

    def test_document_type_combo_exists(self):
        """Существование comboBox типа документа."""
        self.assertIsNotNone(self.dialog.type_combo)

    def test_employee_combo_populated(self):
        """ComboBox сотрудников заполнен."""
        count = self.dialog.employee_combo.count()
        self.assertGreater(count, 0)

    def test_save_creates_document(self):
        """Сохранение создает документ."""
        # Выбираем сотрудника
        self.dialog.employee_combo.setCurrentIndex(0)
        
        # Выбираем тип документа
        type_index = self.dialog.type_combo.findText('Отпуск')
        if type_index >= 0:
            self.dialog.type_combo.setCurrentIndex(type_index)
        
        self.dialog.save()
        
        # Проверяем вызов к БД
        self.mock_db.execute_query.assert_called()
        calls = [call[0][0] for call in self.mock_db.execute_query.call_args_list]
        # Должен быть INSERT для документа
        self.assertTrue(any('INSERT' in call for call in calls))

    def test_validation_no_employee_selected(self):
        """Валидация: сотрудник не выбран."""
        from PyQt5.QtWidgets import QMessageBox
        
        # Очищаем comboBox
        self.dialog.employee_combo.clear()
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.dialog.save()
            mock_warning.assert_called_once()

    def test_validation_no_document_type(self):
        """Валидация: тип документа не выбран."""
        from PyQt5.QtWidgets import QMessageBox
        
        self.dialog.type_combo.setCurrentIndex(-1)
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.dialog.save()
            mock_warning.assert_called_once()

    def test_validation_dates(self):
        """Валидация: даты документа."""
        from PyQt5.QtWidgets import QMessageBox
        from PyQt5.QtCore import QDate
        
        # Устанавливаем даты (конец раньше начала)
        self.dialog.start_date_edit.setDate(QDate(2026, 3, 15))
        self.dialog.end_date_edit.setDate(QDate(2026, 3, 1))
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.dialog.save()
            mock_warning.assert_called_once()


class TestDialogEdgeCases(unittest.TestCase):
    """Тесты пограничных случаев для диалогов."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def test_employee_dialog_large_rate(self):
        """EmployeeDialog: большая ставка."""
        from ui.dialogs.employee_dialog import EmployeeDialog
        
        mock_db = Mock()
        dialog = EmployeeDialog(mock_db)
        
        # Устанавливаем максимальное значение
        dialog.rate_spinbox.setValue(999.99)
        self.assertEqual(dialog.rate_spinbox.value(), 999.99)
        
        dialog.close()
        dialog.deleteLater()

    def test_employee_dialog_zero_norm_hours(self):
        """EmployeeDialog: нулевые часы нормы."""
        from ui.dialogs.employee_dialog import EmployeeDialog
        
        mock_db = Mock()
        dialog = EmployeeDialog(mock_db)
        
        dialog.norm_hours_spinbox.setValue(0)
        self.assertEqual(dialog.norm_hours_spinbox.value(), 0)
        
        dialog.close()
        dialog.deleteLater()

    def test_timesheet_dialog_same_day(self):
        """TimesheetDialog: одинаковые даты начала и окончания."""
        from ui.dialogs.timesheet_dialog import TimesheetDialog
        from PyQt5.QtCore import QDate
        
        mock_db = Mock()
        dialog = TimesheetDialog(mock_db)
        
        dialog.start_date_edit.setDate(QDate(2026, 3, 15))
        dialog.end_date_edit.setDate(QDate(2026, 3, 15))
        
        # Должно пройти валидацию
        dialog.close()
        dialog.deleteLater()


if __name__ == '__main__':
    unittest.main()
