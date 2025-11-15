from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSignal
from task_planner.bll.models import TeamMember

class MemberDialog(QDialog):
    """Діалог для додавання/редагування члена команди"""

    member_saved = pyqtSignal(object)

    def __init__(self, project_manager, member=None, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.member = member
        self.setup_ui()

    def setup_ui(self):
        """Налаштовує інтерфейс діалогу"""
        self.setWindowTitle("Редагування члена команди" if self.member else "Додавання члена команди")
        self.setModal(True)
        self.resize(300, 150)

        layout = QVBoxLayout()

        # Ім'я
        layout.addWidget(QLabel("Ім'я*:"))
        self.name_edit = QLineEdit()
        if self.member:
            self.name_edit.setText(self.member.name)
        layout.addWidget(self.name_edit)

        # Роль
        layout.addWidget(QLabel("Роль*:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Розробник", "Тестувальник", "Дизайнер", "Менеджер", "Аналітик"])
        if self.member:
            index = self.role_combo.findText(self.member.role)
            if index >= 0:
                self.role_combo.setCurrentIndex(index)
        layout.addWidget(self.role_combo)

        # Кнопки
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Зберегти")
        self.cancel_button = QPushButton("Скасувати")

        self.save_button.clicked.connect(self.save_member)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_member(self):
        """Зберігає члена команди"""
        try:
            name = self.name_edit.text().strip()
            role = self.role_combo.currentText()

            # Валідація
            if not name:
                QMessageBox.warning(self, "Помилка", "Ім'я не може бути порожнім")
                return

            if not role:
                QMessageBox.warning(self, "Помилка", "Роль не може бути порожньою")
                return

            if self.member:
                # Редагування існуючого члена команди
                self.member.name = name
                self.member.role = role
            else:
                # Створення нового члена команди
                from task_planner.bll.models import TeamMember
                member = TeamMember(name=name, role=role)
                self.project_manager.add_member(member)
                self.member = member

            self.member_saved.emit(self.member)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти члена команди: {str(e)}")