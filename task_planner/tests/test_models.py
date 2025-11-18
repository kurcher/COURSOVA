import pytest
from datetime import date, datetime, timedelta
from task_planner.bll.models.task import Task
from task_planner.bll.models.team_member import TeamMember
from task_planner.bll.exceptions import TaskValidationError, MemberValidationError


# Фікстури для моделей
@pytest.fixture
def sample_task_data():
    return {
        'title': 'Test Task',
        'description': 'Test Description',
        'deadline': date.today() + timedelta(days=7)
    }


@pytest.fixture
def sample_member_data():
    return {
        'name': 'John Doe',
        'role': 'Розробник'
    }


class TestTaskModel:
    """Тести для моделі Task"""

    def test_create_task_valid_data(self, sample_task_data):
        """Тест створення завдання з валідними даними"""
        # Arrange
        title = sample_task_data['title']
        description = sample_task_data['description']
        deadline = sample_task_data['deadline']

        # Act
        task = Task(title=title, description=description, deadline=deadline)

        # Assert
        assert task.title == title
        assert task.description == description
        assert task.deadline == deadline
        assert task.is_completed is False
        assert task.assignee_id is None
        assert task.id is not None
        assert isinstance(task.created_date, datetime)

    def test_create_task_empty_title_raises_error(self, sample_task_data):
        """Тест створення завдання з порожньою назвою"""
        # Arrange
        sample_task_data['title'] = '   '  # Пробіли теж вважаються порожніми

        # Act & Assert
        with pytest.raises(TaskValidationError, match="Назва завдання не може бути порожньою"):
            Task(**sample_task_data)

    def test_create_task_past_deadline_raises_error(self, sample_task_data):
        """Тест створення завдання з минулим дедлайном"""
        # Arrange
        sample_task_data['deadline'] = date.today() - timedelta(days=1)

        # Act & Assert
        with pytest.raises(TaskValidationError, match="Дедлайн не може бути в минулому"):
            Task(**sample_task_data)

    def test_mark_task_done(self, sample_task_data):
        """Тест позначення завдання як виконаного"""
        # Arrange
        task = Task(**sample_task_data)
        original_updated_date = task.updated_date

        # Act
        task.mark_done()

        # Assert
        assert task.is_completed is True
        assert task.updated_date >= original_updated_date

    def test_mark_task_undone(self, sample_task_data):
        """Тест позначення завдання як невиконаного"""
        # Arrange
        task = Task(**sample_task_data)
        task.mark_done()  # Спочатку позначаємо як виконане

        # Act
        task.mark_undone()

        # Assert
        assert task.is_completed is False

    def test_is_overdue_future_deadline(self, sample_task_data):
        """Тест перевірки простроченості для майбутнього дедлайну"""
        # Arrange
        task = Task(**sample_task_data)

        # Act
        is_overdue = task.is_overdue()

        # Assert
        assert is_overdue is False

    def test_is_overdue_past_deadline_not_completed(self):
        """Тест перевірки простроченості для минулого дедлайну незавершеного завдання"""
        # Arrange
        # Створюємо завдання з майбутнім дедлайном, потім змінюємо deadline через атрибут
        task = Task(
            title='Overdue Task',
            description='Test Description',
            deadline=date.today() + timedelta(days=1)
        )
        # Змінюємо deadline напряму (обхід валідації)
        task.deadline = date.today() - timedelta(days=1)

        # Act
        is_overdue = task.is_overdue()

        # Assert
        assert is_overdue is True

    def test_is_overdue_past_deadline_completed(self):
        """Тест перевірки простроченості для минулого дедлайну завершеного завдання"""
        # Arrange
        # Створюємо завдання з майбутнім дедлайном
        task = Task(
            title='Completed Overdue Task',
            description='Test Description',
            deadline=date.today() + timedelta(days=1)
        )
        # Змінюємо deadline напряму і позначаємо як виконане
        task.deadline = date.today() - timedelta(days=1)
        task.mark_done()

        # Act
        is_overdue = task.is_overdue()

        # Assert
        assert is_overdue is False

    def test_to_dict(self, sample_task_data):
        """Тест серіалізації завдання в словник"""
        # Arrange
        task = Task(**sample_task_data)

        # Act
        task_dict = task.to_dict()

        # Assert
        assert task_dict['title'] == sample_task_data['title']
        assert task_dict['description'] == sample_task_data['description']
        assert task_dict['deadline'] == sample_task_data['deadline'].isoformat()
        assert task_dict['is_completed'] is False
        assert 'id' in task_dict
        assert 'created_date' in task_dict
        assert 'updated_date' in task_dict

    def test_from_dict(self, sample_task_data):
        """Тест десеріалізації завдання зі словника"""
        # Arrange
        original_task = Task(**sample_task_data)
        task_dict = original_task.to_dict()

        # Act
        restored_task = Task.from_dict(task_dict)

        # Assert
        assert restored_task.title == original_task.title
        assert restored_task.description == original_task.description
        assert restored_task.deadline == original_task.deadline
        assert restored_task.is_completed == original_task.is_completed
        assert restored_task.id == original_task.id


class TestTeamMemberModel:
    """Тести для моделі TeamMember"""

    def test_create_member_valid_data(self, sample_member_data):
        """Тест створення члена команди з валідними даними"""
        # Arrange
        name = sample_member_data['name']
        role = sample_member_data['role']

        # Act
        member = TeamMember(name=name, role=role)

        # Assert
        assert member.name == name
        assert member.role == role
        assert member.task_ids == []
        assert member.id is not None
        assert isinstance(member.created_date, datetime)

    def test_create_member_empty_name_raises_error(self, sample_member_data):
        """Тест створення члена команди з порожнім іменем"""
        # Arrange
        sample_member_data['name'] = '   '

        # Act & Assert
        with pytest.raises(MemberValidationError, match="Ім'я члена команди не може бути порожнім"):
            TeamMember(**sample_member_data)

    def test_create_member_empty_role_raises_error(self, sample_member_data):
        """Тест створення члена команди з порожньою роллю"""
        # Arrange
        sample_member_data['role'] = '   '

        # Act & Assert
        with pytest.raises(MemberValidationError, match="Роль члена команди не може бути порожньою"):
            TeamMember(**sample_member_data)

    def test_add_task(self, sample_member_data):
        """Тест додавання завдання члену команди"""
        # Arrange
        member = TeamMember(**sample_member_data)
        task_id = "test-task-id"
        original_updated_date = member.updated_date

        # Act
        member.add_task(task_id)

        # Assert
        assert task_id in member.task_ids
        assert len(member.task_ids) == 1
        assert member.updated_date >= original_updated_date

    def test_add_duplicate_task(self, sample_member_data):
        """Тест додавання дубльованого завдання"""
        # Arrange
        member = TeamMember(**sample_member_data)
        task_id = "test-task-id"
        member.add_task(task_id)
        task_count_before = len(member.task_ids)

        # Act
        member.add_task(task_id)  # Додаємо той самий ID знову

        # Assert
        assert len(member.task_ids) == task_count_before  # Кількість не змінилась

    def test_remove_task(self, sample_member_data):
        """Тест видалення завдання у члена команди"""
        # Arrange
        member = TeamMember(**sample_member_data)
        task_id = "test-task-id"
        member.add_task(task_id)

        # Act
        member.remove_task(task_id)

        # Assert
        assert task_id not in member.task_ids
        assert len(member.task_ids) == 0

    def test_remove_nonexistent_task(self, sample_member_data):
        """Тест видалення неіснуючого завдання"""
        # Arrange
        member = TeamMember(**sample_member_data)
        task_count_before = len(member.task_ids)

        # Act
        member.remove_task("nonexistent-task-id")

        # Assert
        assert len(member.task_ids) == task_count_before  # Кількість не змінилась

    def test_get_workload(self, sample_member_data):
        """Тест отримання навантаження члена команди"""
        # Arrange
        member = TeamMember(**sample_member_data)
        member.add_task("task-1")
        member.add_task("task-2")

        # Act
        workload = member.get_workload()

        # Assert
        assert workload == 2

    def test_to_dict(self, sample_member_data):
        """Тест серіалізації члена команди в словник"""
        # Arrange
        member = TeamMember(**sample_member_data)
        member.add_task("task-1")

        # Act
        member_dict = member.to_dict()

        # Assert
        assert member_dict['name'] == sample_member_data['name']
        assert member_dict['role'] == sample_member_data['role']
        assert member_dict['task_ids'] == ['task-1']
        assert 'id' in member_dict
        assert 'created_date' in member_dict
        assert 'updated_date' in member_dict

    def test_from_dict(self, sample_member_data):
        """Тест десеріалізації члена команди зі словника"""
        # Arrange
        original_member = TeamMember(**sample_member_data)
        original_member.add_task("task-1")
        member_dict = original_member.to_dict()

        # Act
        restored_member = TeamMember.from_dict(member_dict)

        # Assert
        assert restored_member.name == original_member.name
        assert restored_member.role == original_member.role
        assert restored_member.task_ids == original_member.task_ids
        assert restored_member.id == original_member.id