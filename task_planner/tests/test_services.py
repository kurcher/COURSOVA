import pytest
from datetime import date, timedelta
from task_planner.bll.models import Task, TeamMember
from task_planner.bll.services import ProjectManager
from task_planner.bll.exceptions import (
    DuplicateMemberError, DuplicateTaskError,
    MemberNotFoundError, TaskNotFoundError
)


class TestProjectManager:
    """Тести для класу ProjectManager (~70% покриття)"""

    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.manager = ProjectManager()

        # Додаємо тестового члена команди
        self.member = TeamMember(name="Тестовий член", role="Розробник")
        self.manager.members.append(self.member)

        # Додаємо тестове завдання
        self.task = Task(
            title="Тестове завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )
        self.manager.tasks.append(self.task)

    def test_initial_state(self):
        """Тест початкового стану менеджера (Triple A)"""
        # Arrange & Act
        manager = ProjectManager()

        # Assert
        assert manager.members == []
        assert manager.tasks == []

    def test_add_member_success(self):
        """Тест успішного додавання члена команди (Triple A)"""
        # Arrange
        new_member = TeamMember(name="Новий член", role="Дизайнер")

        # Act
        self.manager.add_member(new_member)

        # Assert
        assert len(self.manager.members) == 2
        assert new_member in self.manager.members

    def test_add_duplicate_member(self):
        """Тест додавання члена команди з дублюючим іменем (Triple A)"""
        # Arrange
        duplicate_member = TeamMember(name=self.member.name, role="Аналітик")

        # Act & Assert
        with pytest.raises(DuplicateMemberError):
            self.manager.add_member(duplicate_member)

    def test_add_task_success(self):
        """Тест успішного додавання завдання (Triple A)"""
        # Arrange
        new_task = Task(
            title="Нове завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=2)
        )

        # Act
        self.manager.add_task(new_task)

        # Assert
        assert len(self.manager.tasks) == 2
        assert new_task in self.manager.tasks

    def test_add_task_with_assignee(self):
        """Тест додавання завдання з виконавцем (Triple A)"""
        # Arrange
        new_task = Task(
            title="Завдання з виконавцем",
            description="Опис",
            deadline=date.today() + timedelta(days=2),
            assignee_id=self.member.id
        )

        # Act
        self.manager.add_task(new_task)

        # Assert
        assert new_task in self.manager.tasks
        assert new_task.id in self.member.task_ids

    def test_add_duplicate_task(self):
        """Тест додавання завдання з дублюючою назвою (Triple A)"""
        # Arrange
        duplicate_task = Task(
            title=self.task.title,
            description="Інший опис",
            deadline=date.today() + timedelta(days=2)
        )

        # Act & Assert
        with pytest.raises(DuplicateTaskError):
            self.manager.add_task(duplicate_task)

    def test_remove_member_with_tasks(self):
        """Тест видалення члена команди з завданнями (Triple A)"""
        # Arrange
        self.manager.update_task_assignee(self.task.id, self.member.id)

        # Act
        self.manager.remove_member(self.member.id)

        # Assert
        assert len(self.manager.members) == 0
        assert len(self.manager.tasks) == 0  # Завдання також видаляються

    def test_remove_member_without_tasks(self):
        """Тест видалення члена команди без завдань (Triple A)"""
        # Arrange - завдання не призначене члену команди
        assert self.task.assignee_id is None

        # Act
        self.manager.remove_member(self.member.id)

        # Assert
        assert len(self.manager.members) == 0
        assert len(self.manager.tasks) == 1  # Завдання залишається

    def test_remove_task(self):
        """Тест видалення завдання (Triple A)"""
        # Act
        self.manager.remove_task(self.task.id)

        # Assert
        assert len(self.manager.tasks) == 0

    def test_update_task_assignee(self):
        """Тест оновлення призначеного виконавця (Triple A)"""
        # Act - призначити виконавця
        self.manager.update_task_assignee(self.task.id, self.member.id)

        # Assert
        assert self.task.assignee_id == self.member.id
        assert self.task.id in self.member.task_ids

        # Act - видалити призначення
        self.manager.update_task_assignee(self.task.id, None)

        # Assert
        assert self.task.assignee_id is None
        assert self.task.id not in self.member.task_ids

    def test_find_methods(self):
        """Тест методів пошуку (Triple A)"""
        # Act & Assert - пошук члена команди
        found_member = self.manager.find_member_by_id(self.member.id)
        assert found_member == self.member

        found_member = self.manager.find_member_by_name(self.member.name)
        assert found_member == self.member

        # Act & Assert - пошук завдання
        found_task = self.manager.find_task_by_id(self.task.id)
        assert found_task == self.task

    def test_get_member_tasks(self):
        """Тест отримання завдань члена команди (Triple A)"""
        # Arrange
        self.manager.update_task_assignee(self.task.id, self.member.id)

        # Act
        member_tasks = self.manager.get_member_tasks(self.member.id)

        # Assert
        assert len(member_tasks) == 1
        assert member_tasks[0] == self.task

    def test_get_project_progress(self):
        """Тест розрахунку прогресу проєкту (Triple A)"""
        # Act & Assert - початковий прогрес
        assert self.manager.get_project_progress() == 0.0

        # Arrange - позначаємо завдання виконаним
        self.task.mark_done()

        # Act & Assert - прогрес 100%
        assert self.manager.get_project_progress() == 100.0

        # Arrange - додаємо ще одне завдання
        another_task = Task(
            title="Інше завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )
        self.manager.tasks.append(another_task)

        # Act & Assert - прогрес 50%
        assert self.manager.get_project_progress() == 50.0

    def test_get_tasks_by_status(self):
        """Тест отримання завдань за статусом (Triple A)"""
        # Act & Assert - невиконані завдання
        pending_tasks = self.manager.get_pending_tasks()
        assert len(pending_tasks) == 1
        assert pending_tasks[0] == self.task

        # Act & Assert - виконані завдання (поки немає)
        completed_tasks = self.manager.get_completed_tasks()
        assert len(completed_tasks) == 0

        # Arrange - позначаємо як виконане
        self.task.mark_done()

        # Act & Assert - тепер є виконані
        completed_tasks = self.manager.get_completed_tasks()
        assert len(completed_tasks) == 1

    def test_get_overdue_tasks(self):
        """Тест отримання прострочених завдань (Triple A)"""
        # Act & Assert - спочатку немає прострочених
        overdue_tasks = self.manager.get_overdue_tasks()
        assert len(overdue_tasks) == 0

        # Arrange - робимо завдання простроченим
        self.task.deadline = date.today() - timedelta(days=1)

        # Act & Assert - тепер є прострочені
        overdue_tasks = self.manager.get_overdue_tasks()
        assert len(overdue_tasks) == 1
        assert overdue_tasks[0] == self.task



    def test_add_task_with_nonexistent_assignee(self):
        """Тест додавання завдання з неіснуючим виконавцем (Triple A)"""
        # Arrange
        manager = ProjectManager()
        task = Task(
            title="Завдання з неіснуючим виконавцем",
            description="Опис",
            deadline=date.today() + timedelta(days=1),
            assignee_id="nonexistent-id"
        )

        # Act & Assert
        with pytest.raises(MemberNotFoundError):
            manager.add_task(task)

    def test_remove_nonexistent_member(self):
        """Тест видалення неіснуючого члена команди (Triple A)"""
        # Arrange
        manager = ProjectManager()

        # Act & Assert
        with pytest.raises(MemberNotFoundError):
            manager.remove_member("nonexistent-id")

    def test_remove_nonexistent_task(self):
        """Тест видалення неіснуючого завдання (Triple A)"""
        # Arrange
        manager = ProjectManager()

        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            manager.remove_task("nonexistent-id")

    def test_update_task_assignee_nonexistent_task(self):
        """Тест оновлення виконавця для неіснуючого завдання (Triple A)"""
        # Arrange
        manager = ProjectManager()
        member = TeamMember(name="Тестовий член", role="Розробник")
        manager.add_member(member)

        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            manager.update_task_assignee("nonexistent-task-id", member.id)

    def test_update_task_assignee_nonexistent_member(self):
        """Тест оновлення виконавця на неіснуючого члена команди (Triple A)"""
        # Arrange
        manager = ProjectManager()
        task = Task(
            title="Тестове завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )
        manager.add_task(task)

        # Act & Assert
        with pytest.raises(MemberNotFoundError):
            manager.update_task_assignee(task.id, "nonexistent-member-id")

    def test_get_member_tasks_empty(self):
        """Тест отримання завдань члена команди без завдань (Triple A)"""
        # Arrange
        manager = ProjectManager()
        member = TeamMember(name="Тестовий член", role="Розробник")
        manager.add_member(member)

        # Act
        tasks = manager.get_member_tasks(member.id)

        # Assert
        assert tasks == []

    def test_get_project_progress_empty(self):
        """Тест прогресу проєкту без завдань (Triple A)"""
        # Arrange
        manager = ProjectManager()

        # Act
        progress = manager.get_project_progress()

        # Assert
        assert progress == 0.0