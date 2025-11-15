import pytest
import sys
import os
from datetime import date, timedelta

# Додаємо кореневу папку проєкту до шляху Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from task_planner.bll.models import Task, TeamMember, TaskError, MemberError
from task_planner.bll.services import ProjectManager


class TestTask:
    """Тести для класу Task"""

    def test_create_task_valid(self):
        """Тест створення коректного завдання"""
        task = Task(
            title="Тестове завдання",
            description="Опис тестового завдання",
            deadline=date.today() + timedelta(days=7)
        )

        assert task.title == "Тестове завдання"
        assert task.description == "Опис тестового завдання"
        assert task.deadline == date.today() + timedelta(days=7)
        assert not task.is_completed
        assert task.assignee_id is None

    def test_create_task_empty_title(self):
        """Тест створення завдання з порожньою назвою"""
        with pytest.raises(TaskError, match="Назва завдання не може бути порожньою"):
            Task(
                title="",
                description="Опис",
                deadline=date.today() + timedelta(days=1)
            )

    def test_create_task_past_deadline(self):
        """Тест створення завдання з минулим дедлайном"""
        with pytest.raises(TaskError, match="Дедлайн не може бути в минулому"):
            Task(
                title="Тестове завдання",
                description="Опис",
                deadline=date.today() - timedelta(days=1)
            )

    def test_mark_done(self):
        """Тест позначення завдання як виконаного"""
        task = Task(
            title="Тестове завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )

        task.mark_done()
        assert task.is_completed

    def test_mark_undone(self):
        """Тест позначення завдання як невиконаного"""
        task = Task(
            title="Тестове завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )

        task.mark_done()
        task.mark_undone()
        assert not task.is_completed

    def test_is_overdue(self):
        """Тест перевірки простроченості завдання"""
        # Створюємо завдання з майбутнім дедлайном
        task = Task(
            title="Тестове завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )
        assert not task.is_overdue()

        # Змінюємо дедлайн на минулий (обходимо валідацію __post_init__)
        task.deadline = date.today() - timedelta(days=1)
        assert task.is_overdue()

        # Виконане завдання з минулим дедлайном
        task.mark_done()
        assert not task.is_overdue()

    def test_to_dict(self):
        """Тест серіалізації завдання у словник"""
        task = Task(
            title="Тестове завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )

        task_dict = task.to_dict()

        assert task_dict['title'] == "Тестове завдання"
        assert task_dict['description'] == "Опис"
        assert task_dict['is_completed'] is False
        assert 'id' in task_dict

    def test_from_dict(self):
        """Тест десеріалізації завдання зі словника"""
        task_data = {
            'id': 'test-id',
            'title': 'Тестове завдання',
            'description': 'Опис',
            'deadline': (date.today() + timedelta(days=1)).isoformat(),
            'is_completed': False,
            'assignee_id': None
        }

        task = Task.from_dict(task_data)

        assert task.id == 'test-id'
        assert task.title == 'Тестове завдання'
        assert task.description == 'Опис'
        assert not task.is_completed


class TestTeamMember:
    """Тести для класу TeamMember"""

    def test_create_member_valid(self):
        """Тест створення коректного члена команди"""
        member = TeamMember(name="Іван Іванов", role="Розробник")

        assert member.name == "Іван Іванов"
        assert member.role == "Розробник"
        assert member.task_ids == []

    def test_create_member_empty_name(self):
        """Тест створення члена команди з порожнім іменем"""
        with pytest.raises(MemberError, match="Ім'я члена команди не може бути порожнім"):
            TeamMember(name="", role="Розробник")

    def test_create_member_empty_role(self):
        """Тест створення члена команди з порожньою роллю"""
        with pytest.raises(MemberError, match="Роль члена команди не може бути порожньою"):
            TeamMember(name="Іван Іванов", role="")

    def test_add_remove_task(self):
        """Тест додавання та видалення завдань"""
        member = TeamMember(name="Іван Іванов", role="Розробник")
        task_id = "task-123"

        member.add_task(task_id)
        assert task_id in member.task_ids
        assert member.get_workload() == 1

        member.remove_task(task_id)
        assert task_id not in member.task_ids
        assert member.get_workload() == 0

    def test_to_dict(self):
        """Тест серіалізації члена команди у словник"""
        member = TeamMember(name="Іван Іванов", role="Розробник")

        member_dict = member.to_dict()

        assert member_dict['name'] == "Іван Іванов"
        assert member_dict['role'] == "Розробник"
        assert 'id' in member_dict
        assert member_dict['task_ids'] == []


class TestProjectManager:
    """Тести для класу ProjectManager"""

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



    def test_add_duplicate_member(self):
        """Тест додавання члена команди з дублюючим іменем"""
        with pytest.raises(MemberError):
            duplicate_member = TeamMember(name="Тестовий член", role="Аналітик")
            self.manager.add_member(duplicate_member)

    def test_add_duplicate_task(self):
        """Тест додавання завдання з дублюючою назвою"""
        with pytest.raises(TaskError):
            duplicate_task = Task(
                title="Тестове завдання",
                description="Інший опис",
                deadline=date.today() + timedelta(days=2)
            )
            self.manager.add_task(duplicate_task)

    def test_remove_member(self):
        """Тест видалення члена команди"""
        # Спочатку призначимо завдання члену команди
        self.manager.update_task_assignee(self.task.id, self.member.id)

        # Тепер видаляємо члена команди
        self.manager.remove_member(self.member.id)
        assert len(self.manager.members) == 0
        # Завдання також має бути видалено, оскільки воно було призначене цьому члену команди
        assert len(self.manager.tasks) == 0

    def test_remove_member_without_tasks(self):
        """Тест видалення члена команди без завдань"""
        # Завдання не призначене члену команди
        assert self.task.assignee_id is None

        # Видаляємо члена команди
        self.manager.remove_member(self.member.id)
        assert len(self.manager.members) == 0
        # Завдання має залишитися, оскільки воно не було призначене видаленому члену команди
        assert len(self.manager.tasks) == 1

    def test_remove_task(self):
        """Тест видалення завдання"""
        self.manager.remove_task(self.task.id)
        assert len(self.manager.tasks) == 0

    def test_update_task_assignee(self):
        """Тест оновлення призначеного виконавця"""
        # Призначаємо завдання члену команди
        self.manager.update_task_assignee(self.task.id, self.member.id)

        assert self.task.assignee_id == self.member.id
        assert self.task.id in self.member.task_ids

        # Видаляємо призначення
        self.manager.update_task_assignee(self.task.id, None)

        assert self.task.assignee_id is None
        assert self.task.id not in self.member.task_ids

    def test_get_member_tasks(self):
        """Тест отримання завдань члена команди"""
        self.manager.update_task_assignee(self.task.id, self.member.id)

        member_tasks = self.manager.get_member_tasks(self.member.id)
        assert len(member_tasks) == 1
        assert member_tasks[0].id == self.task.id

    def test_get_overdue_tasks(self):
        """Тест отримання прострочених завдань"""
        # Створюємо прострочене завдання
        overdue_task = Task(
            title="Прострочене завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)  # Спочатку майбутній дедлайн
        )
        overdue_task.deadline = date.today() - timedelta(days=1)  # Змінюємо на минулий
        self.manager.tasks.append(overdue_task)

        overdue_tasks = self.manager.get_overdue_tasks()
        assert len(overdue_tasks) == 1
        assert overdue_tasks[0].title == "Прострочене завдання"

    def test_get_completed_tasks(self):
        """Тест отримання виконаних завдань"""
        self.task.mark_done()

        completed_tasks = self.manager.get_completed_tasks()
        assert len(completed_tasks) == 1
        assert completed_tasks[0].id == self.task.id

    def test_get_pending_tasks(self):
        """Тест отримання незавершених завдань"""
        pending_tasks = self.manager.get_pending_tasks()
        assert len(pending_tasks) == 1
        assert pending_tasks[0].id == self.task.id

    def test_get_project_progress(self):
        """Тест розрахунку прогресу проєкту"""
        # Спочатку 0% (немає виконаних завдань)
        assert self.manager.get_project_progress() == 0.0

        # Позначаємо завдання як виконане
        self.task.mark_done()
        assert self.manager.get_project_progress() == 100.0

        # Додаємо ще одне невиконане завдання
        another_task = Task(
            title="Інше завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )
        self.manager.tasks.append(another_task)

        assert self.manager.get_project_progress() == 50.0

    def test_find_member_by_id(self):
        """Тест пошуку члена команди за ID"""
        found_member = self.manager.find_member_by_id(self.member.id)
        assert found_member == self.member

    def test_find_member_by_name(self):
        """Тест пошуку члена команди за іменем"""
        found_member = self.manager.find_member_by_name("Тестовий член")
        assert found_member == self.member

    def test_find_task_by_id(self):
        """Тест пошуку завдання за ID"""
        found_task = self.manager.find_task_by_id(self.task.id)
        assert found_task == self.task