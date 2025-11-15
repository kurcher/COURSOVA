from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QTableWidget, QTableWidgetItem,
                             QPushButton, QLabel, QProgressBar, QMessageBox,
                             QHeaderView, QSplitter, QComboBox, QLineEdit,
                             QCheckBox, QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import date



class MainWindow(QMainWindow):
    """Головне вікно програми"""





    def __init__(self, project_manager, dal):
        super().__init__()
        self.project_manager = project_manager
        self.dal = dal
        self.setup_ui()
        self.load_data()
        self.update_ui()

    def setup_ui(self):
        """Налаштовує інтерфейс головного вікна"""
        self.setWindowTitle("Планувальник завдань")
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Панель статусу проєкту
        status_layout = QHBoxLayout()

        self.progress_label = QLabel("Прогрес проєкту:")
        status_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        status_layout.addWidget(self.progress_bar)

        self.stats_label = QLabel()
        status_layout.addWidget(self.stats_label)

        status_layout.addStretch()

        main_layout.addLayout(status_layout)

        # Основні вкладки
        self.tabs = QTabWidget()

        # Вкладка завдань
        self.tasks_tab = QWidget()
        self.setup_tasks_tab()
        self.tabs.addTab(self.tasks_tab, "Завдання")

        # Вкладка членів команди
        self.members_tab = QWidget()
        self.setup_members_tab()
        self.tabs.addTab(self.members_tab, "Члени команди")

        main_layout.addWidget(self.tabs)

    def setup_tasks_tab(self):
        """Налаштовує вкладку завдань"""
        layout = QVBoxLayout(self.tasks_tab)

        # Панель керування завданнями
        control_layout = QHBoxLayout()

        self.add_task_button = QPushButton("Додати завдання")
        self.add_task_button.clicked.connect(self.add_task)
        control_layout.addWidget(self.add_task_button)

        self.edit_task_button = QPushButton("Редагувати")
        self.edit_task_button.clicked.connect(self.edit_task)
        control_layout.addWidget(self.edit_task_button)

        self.delete_task_button = QPushButton("Видалити")
        self.delete_task_button.clicked.connect(self.delete_task)
        control_layout.addWidget(self.delete_task_button)

        control_layout.addStretch()

        # Фільтри
        control_layout.addWidget(QLabel("Фільтр:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Всі", "Активні", "Прострочені", "Виконані"])
        self.filter_combo.currentTextChanged.connect(self.update_tasks_table)
        control_layout.addWidget(self.filter_combo)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Пошук...")
        self.search_edit.textChanged.connect(self.update_tasks_table)
        control_layout.addWidget(self.search_edit)

        layout.addLayout(control_layout)

        # Таблиця завдань
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(6)
        self.tasks_table.setHorizontalHeaderLabels([
            "Назва", "Опис", "Дедлайн", "Виконавець", "Статус", "Прострочено"
        ])
        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tasks_table.doubleClicked.connect(self.edit_task)
        layout.addWidget(self.tasks_table)



    def setup_members_tab(self):
        """Налаштовує вкладку членів команди"""
        layout = QVBoxLayout(self.members_tab)

        # Панель керування членами команди
        control_layout = QHBoxLayout()

        self.add_member_button = QPushButton("Додати члена команди")
        self.add_member_button.clicked.connect(self.add_member)
        control_layout.addWidget(self.add_member_button)

        self.edit_member_button = QPushButton("Редагувати")
        self.edit_member_button.clicked.connect(self.edit_member)
        control_layout.addWidget(self.edit_member_button)

        self.delete_member_button = QPushButton("Видалити")
        self.delete_member_button.clicked.connect(self.delete_member)
        control_layout.addWidget(self.delete_member_button)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Таблиця членів команди
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(4)
        self.members_table.setHorizontalHeaderLabels([
            "Ім'я", "Роль", "Кількість завдань", "Завантаженість"
        ])
        self.members_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.members_table.doubleClicked.connect(self.edit_member)
        layout.addWidget(self.members_table)

    def load_data(self):
        """Завантажує дані з DAL"""
        try:
            # Завантажуємо членів команди
            members_data = self.dal.load_members()
            for member_data in members_data:
                member = self.project_manager.find_member_by_id(member_data['id'])
                if not member:

                    from task_planner.bll.models import TeamMember
                    member = TeamMember.from_dict(member_data)
                    self.project_manager.members.append(member)

            # Завантажуємо завдання
            tasks_data = self.dal.load_tasks()
            for task_data in tasks_data:
                task = self.project_manager.find_task_by_id(task_data['id'])
                if not task:

                    from task_planner.bll.models import Task
                    task = Task.from_dict(task_data)
                    self.project_manager.tasks.append(task)

                    # Відновлюємо зв'язок з виконавцем
                    if task.assignee_id:
                        assignee = self.project_manager.find_member_by_id(task.assignee_id)
                        if assignee:
                            assignee.add_task(task.id)

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити дані: {str(e)}")

    def save_data(self):
        """Зберігає дані через DAL"""
        try:
            members_data = [member.to_dict() for member in self.project_manager.members]
            tasks_data = [task.to_dict() for task in self.project_manager.tasks]

            self.dal.save_members(members_data)
            self.dal.save_tasks(tasks_data)

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти дані: {str(e)}")

    def update_ui(self):
        """Оновлює весь інтерфейс"""
        self.update_tasks_table()
        self.update_members_table()
        self.update_project_status()

    def update_tasks_table(self):
        """Оновлює таблицю завдань"""
        self.tasks_table.setRowCount(0)

        # Фільтрація завдань
        filter_text = self.filter_combo.currentText()
        search_text = self.search_edit.text().lower()

        filtered_tasks = []
        for task in self.project_manager.tasks:
            # Застосовуємо фільтр статусу
            if filter_text == "Активні" and task.is_completed:
                continue
            elif filter_text == "Прострочені" and not task.is_overdue():
                continue
            elif filter_text == "Виконані" and not task.is_completed:
                continue

            # Застосовуємо пошук
            if search_text:
                task_text = f"{task.title} {task.description}".lower()
                if search_text not in task_text:
                    continue

            filtered_tasks.append(task)

        # Заповнення таблиці
        self.tasks_table.setRowCount(len(filtered_tasks))
        for row, task in enumerate(filtered_tasks):
            # Назва
            title_item = QTableWidgetItem(task.title)
            self.tasks_table.setItem(row, 0, title_item)

            # Опис
            desc_item = QTableWidgetItem(task.description)
            self.tasks_table.setItem(row, 1, desc_item)

            # Дедлайн
            deadline_item = QTableWidgetItem(task.deadline.strftime("%d.%m.%Y"))
            self.tasks_table.setItem(row, 2, deadline_item)

            # Виконавець
            assignee_name = "Не призначено"
            if task.assignee_id:
                assignee = self.project_manager.find_member_by_id(task.assignee_id)
                if assignee:
                    assignee_name = assignee.name
            assignee_item = QTableWidgetItem(assignee_name)
            self.tasks_table.setItem(row, 3, assignee_item)

            # Статус
            status_item = QTableWidgetItem("Виконано" if task.is_completed else "Активне")
            self.tasks_table.setItem(row, 4, status_item)

            # Прострочено
            overdue_text = "Так" if task.is_overdue() else "Ні"
            overdue_item = QTableWidgetItem(overdue_text)
            if task.is_overdue():
                overdue_item.setForeground(Qt.red)
            self.tasks_table.setItem(row, 5, overdue_item)

            # Зберігаємо ID завдання для подальшого використання
            for col in range(6):
                self.tasks_table.item(row, col).setData(Qt.UserRole, task.id)

    def update_members_table(self):
        """Оновлює таблицю членів команди"""
        self.members_table.setRowCount(len(self.project_manager.members))

        for row, member in enumerate(self.project_manager.members):
            # Ім'я
            name_item = QTableWidgetItem(member.name)
            self.members_table.setItem(row, 0, name_item)

            # Роль
            role_item = QTableWidgetItem(member.role)
            self.members_table.setItem(row, 1, role_item)

            # Кількість завдань
            tasks_count = member.get_workload()
            tasks_item = QTableWidgetItem(str(tasks_count))
            self.members_table.setItem(row, 2, tasks_item)

            # Завантаженість
            workload_text = "Низька" if tasks_count == 0 else "Середня" if tasks_count < 3 else "Висока"
            if tasks_count >= 5:
                workload_text = "Дуже висока"
            workload_item = QTableWidgetItem(workload_text)
            self.members_table.setItem(row, 3, workload_item)

            # Зберігаємо ID члена команди для подальшого використання
            for col in range(4):
                self.members_table.item(row, col).setData(Qt.UserRole, member.id)

    def update_project_status(self):
        """Оновлює статус проєкту"""
        total_tasks = len(self.project_manager.tasks)
        completed_tasks = len(self.project_manager.get_completed_tasks())
        overdue_tasks = len(self.project_manager.get_overdue_tasks())

        progress = self.project_manager.get_project_progress()
        self.progress_bar.setValue(int(progress))

        stats_text = f"Завдань: {total_tasks} | Виконано: {completed_tasks} | Прострочено: {overdue_tasks}"
        self.stats_label.setText(stats_text)

    def add_task(self):
        """Додає нове завдання"""
        from task_planner.pl.task_dialog import TaskDialog
        dialog = TaskDialog(self.project_manager, self.project_manager.members, parent=self)
        dialog.task_saved.connect(self.on_task_saved)
        dialog.exec_()

    def edit_task(self):
        """Редагує вибране завдання"""
        selected_items = self.tasks_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Попередження", "Будь ласка, виберіть завдання для редагування")
            return

        task_id = selected_items[0].data(Qt.UserRole)
        task = self.project_manager.find_task_by_id(task_id)
        if not task:
            QMessageBox.warning(self, "Попередження", "Завдання не знайдено")
            return

        from task_planner.pl.task_dialog import TaskDialog
        dialog = TaskDialog(self.project_manager, self.project_manager.members, task, self)
        dialog.task_saved.connect(self.on_task_saved)
        dialog.exec_()

    def delete_task(self):
        """Видаляє вибране завдання"""
        selected_items = self.tasks_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Попередження", "Будь ласка, виберіть завдання для видалення")
            return

        task_id = selected_items[0].data(Qt.UserRole)
        task = self.project_manager.find_task_by_id(task_id)
        if not task:
            QMessageBox.warning(self, "Попередження", "Завдання не знайдено")
            return

        reply = QMessageBox.question(
            self,
            "Підтвердження видалення",
            f"Ви впевнені, що хочете видалити завдання '{task.title}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.project_manager.remove_task(task_id)
                self.save_data()
                self.update_ui()
                QMessageBox.information(self, "Успіх", "Завдання успішно видалено")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити завдання: {str(e)}")

    def add_member(self):
        """Додає нового члена команди"""
        from task_planner.pl.member_dialog import MemberDialog
        dialog = MemberDialog(self.project_manager, parent=self)
        dialog.member_saved.connect(self.on_member_saved)
        dialog.exec_()

    def edit_member(self):
        """Редагує вибраного члена команди"""
        selected_items = self.members_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Попередження", "Будь ласка, виберіть члена команди для редагування")
            return

        member_id = selected_items[0].data(Qt.UserRole)
        member = self.project_manager.find_member_by_id(member_id)
        if not member:
            QMessageBox.warning(self, "Попередження", "Члена команди не знайдено")
            return

        from task_planner.pl.member_dialog import MemberDialog
        dialog = MemberDialog(self.project_manager, member, self)
        dialog.member_saved.connect(self.on_member_saved)
        dialog.exec_()

    def delete_member(self):
        """Видаляє вибраного члена команди"""
        selected_items = self.members_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Попередження", "Будь ласка, виберіть члена команди для видалення")
            return

        member_id = selected_items[0].data(Qt.UserRole)
        member = self.project_manager.find_member_by_id(member_id)
        if not member:
            QMessageBox.warning(self, "Попередження", "Члена команди не знайдено")
            return

        if member.get_workload() > 0:
            reply = QMessageBox.question(
                self,
                "Попередження",
                f"Цей член команди має {member.get_workload()} завдань. Видалення призведе до видалення всіх його завдань. Продовжити?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        reply = QMessageBox.question(
            self,
            "Підтвердження видалення",
            f"Ви впевнені, що хочете видалити члена команди '{member.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.project_manager.remove_member(member_id)
                self.save_data()
                self.update_ui()
                QMessageBox.information(self, "Успіх", "Члена команди успішно видалено")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити члена команди: {str(e)}")

    def on_task_saved(self, task):
        """Обробляє збереження завдання"""
        self.save_data()
        self.update_ui()
        QMessageBox.information(self, "Успіх", "Завдання успішно збережено")

    def on_member_saved(self, member):
        """Обробляє збереження члена команди"""
        self.save_data()
        self.update_ui()
        QMessageBox.information(self, "Успіх", "Члена команди успішно збережено")

    def closeEvent(self, event):
        """Обробляє закриття програми"""
        self.save_data()
        event.accept()