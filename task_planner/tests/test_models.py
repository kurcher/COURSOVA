import pytest
from datetime import date, timedelta, datetime
from task_planner.bll.models import Task, TeamMember, TaskError, MemberError


class TestTask:
    """Тести для класу Task (100% покриття)"""

    def test_create_task_valid(self):
        """Тест створення коректного завдання (Triple A)"""
        # Arrange
        title = "Тестове завдання"
        description = "Опис тестового завдання"
        deadline = date.today() + timedelta(days=7)

        # Act
        task = Task(
            title=title,
            description=description,
            deadline=deadline
        )

        # Assert
        assert task.title == title
        assert task.description == description
        assert task.deadline == deadline
        assert not task.is_completed
        assert task.assignee_id is None

    def test_create_task_with_assignee(self):
        """Тест створення завдання з виконавцем (Triple A)"""
        # Arrange
        assignee_id = "test-assignee-123"

        # Act
        task = Task(
            title="Завдання з виконавцем",
            description="Опис",
            deadline=date.today() + timedelta(days=1),
            assignee_id=assignee_id
        )

        # Assert
        assert task.assignee_id == assignee_id

    def test_create_task_auto_fields(self):
        """Тест автоматичного заповнення полів (Triple A)"""
        # Arrange & Act
        task = Task(
            title="Тест авто-полів",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )

        # Assert
        assert task.id is not None
        assert isinstance(task.created_date, datetime)
        assert not task.is_completed

    def test_create_task_empty_title(self):
        """Тест створення завдання з порожньою назвою (Triple A)"""
        # Arrange
        empty_title = ""

        # Act & Assert
        with pytest.raises(TaskError, match="Назва завдання не може бути порожньою"):
            Task(
                title=empty_title,
                description="Опис",
                deadline=date.today() + timedelta(days=1)
            )

    def test_create_task_past_deadline(self):
        """Тест створення завдання з минулим дедлайном (Triple A)"""
        # Arrange
        past_deadline = date.today() - timedelta(days=1)

        # Act & Assert
        with pytest.raises(TaskError, match="Дедлайн не може бути в минулому"):
            Task(
                title="Тестове завдання",
                description="Опис",
                deadline=past_deadline
            )

    def test_mark_done_and_undone(self):
        """Тест зміни статусу виконання (Triple A)"""
        # Arrange
        task = Task(
            title="Тестове завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )

        # Act - позначити виконаним
        task.mark_done()

        # Assert
        assert task.is_completed

        # Act - позначити невиконаним
        task.mark_undone()

        # Assert
        assert not task.is_completed

    def test_is_overdue_scenarios(self):
        """Тест різних сценаріїв простроченості (Triple A)"""
        # Arrange - активне завдання
        task = Task(
            title="Тестове завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )

        # Assert - не прострочене
        assert not task.is_overdue()

        # Arrange - прострочене завдання
        task.deadline = date.today() - timedelta(days=1)

        # Assert - прострочене
        assert task.is_overdue()

        # Arrange - прострочене але виконане
        task.mark_done()

        # Assert - не вважається простроченим
        assert not task.is_overdue()

    def test_to_dict_serialization(self):
        """Тест серіалізації завдання у словник (Triple A)"""
        # Arrange
        task = Task(
            title="Тестове завдання",
            description="Опис",
            deadline=date.today() + timedelta(days=1)
        )

        # Act
        task_dict = task.to_dict()

        # Assert
        expected_fields = ['id', 'title', 'description', 'deadline', 'assignee_id', 'is_completed', 'created_date']
        for field in expected_fields:
            assert field in task_dict

        assert task_dict['title'] == "Тестове завдання"
        assert task_dict['description'] == "Опис"
        assert task_dict['is_completed'] is False

    def test_from_dict_deserialization(self):
        """Тест десеріалізації завдання зі словника (Triple A)"""
        # Arrange
        task_data = {
            'id': 'test-id-123',
            'title': 'Тестове завдання',
            'description': 'Опис',
            'deadline': (date.today() + timedelta(days=1)).isoformat(),
            'is_completed': True,
            'assignee_id': 'assignee-123',
            'created_date': datetime.now().isoformat()
        }

        # Act
        task = Task.from_dict(task_data)

        # Assert
        assert task.id == 'test-id-123'
        assert task.title == 'Тестове завдання'
        assert task.description == 'Опис'
        assert task.is_completed is True
        assert task.assignee_id == 'assignee-123'


class TestTeamMember:
    """Тести для класу TeamMember (~80% покриття)"""

    def test_create_member_valid(self):
        """Тест створення коректного члена команди (Triple A)"""
        # Arrange
        name = "Іван Іванов"
        role = "Розробник"

        # Act
        member = TeamMember(name=name, role=role)

        # Assert
        assert member.name == name
        assert member.role == role
        assert member.task_ids == []

    def test_create_member_auto_id(self):
        """Тест автоматичного генерування ID (Triple A)"""
        # Act
        member = TeamMember(name="Петро Петренко", role="Тестувальник")

        # Assert
        assert member.id is not None
        assert isinstance(member.id, str)
        assert len(member.id) > 0

    def test_create_member_empty_name(self):
        """Тест створення члена команди з порожнім іменем (Triple A)"""
        # Arrange
        empty_name = ""

        # Act & Assert
        with pytest.raises(MemberError, match="Ім'я члена команди не може бути порожнім"):
            TeamMember(name=empty_name, role="Розробник")

    def test_create_member_empty_role(self):
        """Тест створення члена команди з порожньою роллю (Triple A)"""
        # Arrange
        empty_role = ""

        # Act & Assert
        with pytest.raises(MemberError, match="Роль члена команди не може бути порожньою"):
            TeamMember(name="Іван Іванов", role=empty_role)

    def test_add_and_remove_task(self):
        """Тест додавання та видалення завдань (Triple A)"""
        # Arrange
        member = TeamMember(name="Іван Іванов", role="Розробник")
        task_id_1 = "task-123"
        task_id_2 = "task-456"

        # Act - додавання першого завдання
        member.add_task(task_id_1)

        # Assert
        assert task_id_1 in member.task_ids
        assert member.get_workload() == 1

        # Act - додавання другого завдання
        member.add_task(task_id_2)

        # Assert
        assert task_id_2 in member.task_ids
        assert member.get_workload() == 2

        # Act - видалення завдання
        member.remove_task(task_id_1)

        # Assert
        assert task_id_1 not in member.task_ids
        assert task_id_2 in member.task_ids
        assert member.get_workload() == 1

    def test_remove_nonexistent_task(self):
        """Тест видалення неіснуючого завдання (Triple A)"""
        # Arrange
        member = TeamMember(name="Іван Іванов", role="Розробник")

        # Act - видалення неіснуючого завдання
        member.remove_task("nonexistent-task")

        # Assert - не має викликати помилку
        assert member.task_ids == []
        assert member.get_workload() == 0

    def test_get_workload(self):
        """Тест отримання навантаження (Triple A)"""
        # Arrange
        member = TeamMember(name="Іван Іванов", role="Розробник")

        # Assert - початкове навантаження
        assert member.get_workload() == 0

        # Act - додаємо завдання
        member.add_task("task-1")
        member.add_task("task-2")

        # Assert - оновлене навантаження
        assert member.get_workload() == 2

    def test_to_dict_serialization(self):
        """Тест серіалізації члена команди у словник (Triple A)"""
        # Arrange
        member = TeamMember(name="Іван Іванов", role="Розробник")
        member.add_task("task-123")

        # Act
        member_dict = member.to_dict()

        # Assert
        assert member_dict['name'] == "Іван Іванов"
        assert member_dict['role'] == "Розробник"
        assert 'id' in member_dict
        assert member_dict['task_ids'] == ["task-123"]

    def test_from_dict_deserialization(self):
        """Тест десеріалізації члена команди зі словника (Triple A)"""
        # Arrange
        member_data = {
            'id': 'member-id-123',
            'name': 'Петро Петренко',
            'role': 'Тестувальник',
            'task_ids': ['task-1', 'task-2']
        }

        # Act
        member = TeamMember.from_dict(member_data)

        # Assert
        assert member.id == 'member-id-123'
        assert member.name == 'Петро Петренко'  # Виправлено опечатку
        assert member.role == 'Тестувальник'
        assert member.task_ids == ['task-1', 'task-2']