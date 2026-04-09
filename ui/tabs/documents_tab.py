"""
Вкладка управления документами на PyQt5.
ЛР1-Ф2: Ввод плановых неявок.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox, QAbstractItemView
)

from database.models import Document
from services.document_service import DocumentService
from services.employee_service import EmployeeService
from utils.validators import Validator
from ui.dialogs.document_dialog import DocumentDialog


class DocumentsTab(QWidget):
    """Вкладка документов."""

    def __init__(self, db_manager, current_user, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.current_user = current_user
        self.document_service = DocumentService(db_manager)
        self.employee_service = EmployeeService(db_manager)
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Панель действий
        action_layout = QHBoxLayout()

        self.add_btn = QPushButton('Добавить документ')
        self.add_btn.clicked.connect(self.add_document)
        action_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton('Редактировать')
        self.edit_btn.clicked.connect(self.edit_document)
        action_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton('Удалить')
        self.delete_btn.clicked.connect(self.delete_document)
        action_layout.addWidget(self.delete_btn)

        layout.addLayout(action_layout)

        # Таблица документов
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Сотрудник ID', 'Тип документа', 'Дата начала', 'Дата окончания'])

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        self.table.cellDoubleClicked.connect(self.edit_document)

        layout.addWidget(self.table)

        self.load_documents()

    def load_documents(self):
        """Загрузка списка документов."""
        documents = self.document_service.get_all_documents()
        self.table.setRowCount(len(documents))

        for row_idx, doc in enumerate(documents):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(doc.id_document)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(doc.employee_id)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(doc.type))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(doc.start_date)))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(doc.end_date)))

    def get_selected_document_id(self):
        """Получить ID выбранного документа."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            item = self.table.item(row, 0)
            if item:
                return int(item.text())
        return None

    def add_document(self):
        """Добавление документа."""
        dialog = DocumentDialog(self, self.employee_service)
        if dialog.exec() == 1:
            document = dialog.get_document_data()
            self.document_service.add_document(document)
            self.load_documents()
            QMessageBox.information(self, 'Успех', 'Документ добавлен')

    def edit_document(self):
        """Редактирование документа."""
        document_id = self.get_selected_document_id()
        if not document_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите документ')
            return

        documents = self.document_service.get_all_documents()
        doc = next((d for d in documents if d.id_document == document_id), None)

        if doc:
            dialog = DocumentDialog(self, self.employee_service, doc)
            if dialog.exec() == 1:
                updated_doc = dialog.get_document_data()
                updated_doc.id_document = document_id
                self.document_service.update_document(updated_doc)
                self.load_documents()
                QMessageBox.information(self, 'Успех', 'Документ обновлён')

    def delete_document(self):
        """Удаление документа."""
        document_id = self.get_selected_document_id()
        if not document_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите документ')
            return

        reply = QMessageBox.question(
            self, 'Удаление',
            'Вы уверены, что хотите удалить этот документ?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.document_service.delete_document(document_id)
            self.load_documents()
            QMessageBox.information(self, 'Успех', 'Документ удалён')
