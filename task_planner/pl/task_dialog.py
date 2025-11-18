from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QDateEdit, QComboBox,
                             QCheckBox, QPushButton, QMessageBox)
from PyQt5.QtCore import QDate, pyqtSignal
from datetime import date


class TaskDialog(QDialog):
    """Діалог для додавання/редагування завдання"""

    task_saved = pyqtSignal(object)

    def __init__(self, project_manager, members, task=None, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.members = members
        self.task = task
        self.setup_ui()

    def setup_ui(self):
        """Налаштовує інтерфейс діалогу"""
        self.setWindowTitle("Редагування завдання" if self.task else "Додавання завдання")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout()

        # Назва завдання
        layout.addWidget(QLabel("Назва*:"))
        self.title_edit = QLineEdit()
        if self.task:
            self.title_edit.setText(self.task.title)
        layout.addWidget(self.title_edit)

        # Опис завдання
        layout.addWidget(QLabel("Опис:"))
        self.description_edit = QTextEdit()
        if self.task:
            self.description_edit.setText(self.task.description)
        self.description_edit.setMaximumHeight(100)
        layout.addWidget(self.description_edit)

        # Дедлайн
        layout.addWidget(QLabel("Дедлайн*:"))
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setDate(QDate.currentDate().addDays(7))
        self.deadline_edit.setCalendarPopup(True)
        if self.task:
            self.deadline_edit.setDate(QDate(self.task.deadline.year,
                                             self.task.deadline.month,
                                             self.task.deadline.day))
        layout.addWidget(self.deadline_edit)

        # Виконавець
        layout.addWidget(QLabel("Виконавець:"))
        self.assignee_combo = QComboBox()
        self.assignee_combo.addItem("Не призначено", None)
        for member in self.members:
            self.assignee_combo.addItem(f"{member.name} ({member.role})", member.id)

        if self.task and self.task.assignee_id:
            index = self.assignee_combo.findData(self.task.assignee_id)
            if index >= 0:
                self.assignee_combo.setCurrentIndex(index)

        layout.addWidget(self.assignee_combo)

        # Статус виконання
        self.completed_check = QCheckBox("Виконано")
        if self.task:
            self.completed_check.setChecked(self.task.is_completed)
        layout.addWidget(self.completed_check)

        # Кнопки
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Зберегти")
        self.cancel_button = QPushButton("Скасувати")

        self.save_button.clicked.connect(self.save_task)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_task(self):
        """Зберігає завдання"""
        try:
            title = self.title_edit.text().strip()
            description = self.description_edit.toPlainText().strip()
            deadline = self.deadline_edit.date().toPyDate()
            assignee_id = self.assignee_combo.currentData()
            is_completed = self.completed_check.isChecked()

            # Валідація
            if not title:
                QMessageBox.warning(self, "Помилка", "Назва завдання не може бути порожньою")
                return

            if deadline < date.today():
                QMessageBox.warning(self, "Помилка", "Дедлайн не може бути в минулому")
                return

            if self.task:
                # Оновлення існуючого завдання
                # Спочатку оновлюємо призначення
                self.project_manager.update_task_assignee(self.task.id, assignee_id)

                # Потім оновлюємо статус
                if is_completed:
                    self.project_manager.mark_task_done(self.task.id)
                else:
                    self.project_manager.mark_task_undone(self.task.id)

                # Отримуємо оновлене завдання
                self.task = self.project_manager.get_task(self.task.id)
            else:
                # Створення нового завдання
                task = self.project_manager.add_task(
                    title=title,
                    description=description,
                    deadline=deadline,
                    assignee_id=assignee_id
                )

                # Встановлюємо статус
                if is_completed:
                    self.project_manager.mark_task_done(task.id)

                self.task = task

            self.task_saved.emit(self.task)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти завдання: {str(e)}")