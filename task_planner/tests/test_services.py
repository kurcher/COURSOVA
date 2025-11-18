from unittest.mock import Mock, patch

import pytest
import tempfile
import json
import os
from datetime import date, timedelta
from task_planner.bll.models.task import Task
from task_planner.bll.models.team_member import TeamMember
from task_planner.dal.repositories.task_repository import TaskRepository
from task_planner.dal.repositories.member_repository import MemberRepository
from task_planner.bll.services.task_service import TaskService
from task_planner.bll.services.member_service import MemberService
from task_planner.bll.services.project_manager import ProjectManager
from task_planner.bll.exceptions import (
    TaskNotFoundError, MemberNotFoundError,
    DuplicateTaskError, DuplicateMemberError
)


# Фікстури для сервісів
@pytest.fixture
def temp_data_file():
    """Фікстура для тимчасового файлу даних"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"tasks": [], "members": []}, f)
        temp_file = f.name

    yield temp_file
    os.unlink(temp_file)


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


@pytest.fixture
def task_repository(temp_data_file):
    return TaskRepository(temp_data_file)


@pytest.fixture
def member_repository(temp_data_file):
    return MemberRepository(temp_data_file)


@pytest.fixture
def task_service(task_repository, member_repository):
    return TaskService(task_repository, member_repository)


@pytest.fixture
def member_service(member_repository, task_repository):
    return MemberService(member_repository, task_repository)


@pytest.fixture
def project_manager(task_service, member_service):
    return ProjectManager(task_service, member_service)


class TestTaskService:
    """Тести для TaskService"""

    def test_create_task_success(self, task_service, sample_task_data):
        """Тест успішного створення завдання"""
        # Arrange
        title = sample_task_data['title']
        description = sample_task_data['description']
        deadline = sample_task_data['deadline']

        # Act
        task = task_service.create_task(title, description, deadline)

        # Assert
        assert task.title == title
        assert task.description == description
        assert task.deadline == deadline
        assert task.is_completed is False
        assert task.assignee_id is None

    def test_create_task_duplicate_title_raises_error(self, task_service, sample_task_data):
        """Тест створення завдання з дубльованою назвою"""
        # Arrange
        task_service.create_task(**sample_task_data)

        # Act & Assert
        with pytest.raises(DuplicateTaskError):
            task_service.create_task(**sample_task_data)

    def test_create_task_with_assignee(self, task_service, member_service, sample_task_data, sample_member_data):
        """Тест створення завдання з призначеним виконавцем"""
        # Arrange
        member = member_service.create_member(**sample_member_data)

        # Act
        task = task_service.create_task(
            title=sample_task_data['title'],
            description=sample_task_data['description'],
            deadline=sample_task_data['deadline'],
            assignee_id=member.id
        )

        # Assert
        assert task.assignee_id == member.id

    def test_create_task_with_invalid_assignee_raises_error(self, task_service, sample_task_data):
        """Тест створення завдання з неіснуючим виконавцем"""
        # Arrange
        invalid_assignee_id = "non-existent-id"

        # Act & Assert
        with pytest.raises(MemberNotFoundError):
            task_service.create_task(
                title=sample_task_data['title'],
                description=sample_task_data['description'],
                deadline=sample_task_data['deadline'],
                assignee_id=invalid_assignee_id
            )

    def test_get_task_success(self, task_service, sample_task_data):
        """Тест успішного отримання завдання за ID"""
        # Arrange
        created_task = task_service.create_task(**sample_task_data)

        # Act
        retrieved_task = task_service.get_task(created_task.id)

        # Assert
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == created_task.title

    def test_get_nonexistent_task_raises_error(self, task_service):
        """Тест отримання неіснуючого завдання"""
        # Arrange
        non_existent_id = "non-existent-id"

        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            task_service.get_task(non_existent_id)

    def test_get_all_tasks(self, task_service, sample_task_data):
        """Тест отримання всіх завдань"""
        # Arrange
        task1 = task_service.create_task(**sample_task_data)
        task2_data = sample_task_data.copy()
        task2_data['title'] = 'Another Task'
        task2 = task_service.create_task(**task2_data)

        # Act
        all_tasks = task_service.get_all_tasks()

        # Assert
        assert len(all_tasks) == 2
        task_ids = [task.id for task in all_tasks]
        assert task1.id in task_ids
        assert task2.id in task_ids

    def test_mark_task_done(self, task_service, sample_task_data):
        """Тест позначення завдання як виконаного"""
        # Arrange
        task = task_service.create_task(**sample_task_data)

        # Act
        task_service.mark_task_done(task.id)

        # Assert
        updated_task = task_service.get_task(task.id)
        assert updated_task.is_completed is True

    def test_mark_task_undone(self, task_service, sample_task_data):
        """Тест позначення завдання як невиконаного"""
        # Arrange
        task = task_service.create_task(**sample_task_data)
        task_service.mark_task_done(task.id)  # Спочатку позначаємо як виконане

        # Act
        task_service.mark_task_undone(task.id)

        # Assert
        updated_task = task_service.get_task(task.id)
        assert updated_task.is_completed is False

    def test_delete_task(self, task_service, sample_task_data):
        """Тест видалення завдання"""
        # Arrange
        task = task_service.create_task(**sample_task_data)

        # Act
        task_service.delete_task(task.id)

        # Assert
        with pytest.raises(TaskNotFoundError):
            task_service.get_task(task.id)

    def test_get_overdue_tasks(self, task_service, sample_task_data):
        """Тест отримання прострочених завдань"""
        # Arrange
        # Створюємо мок для завдань
        normal_task = Mock(spec=Task)
        normal_task.is_overdue.return_value = False

        overdue_task = Mock(spec=Task)
        overdue_task.is_overdue.return_value = True

        # Мокаємо репозиторій, щоб повернути наші тестові завдання
        with patch.object(task_service._task_repository, 'get_all') as mock_get_all:
            mock_get_all.return_value = [normal_task, overdue_task]

            # Act
            overdue_tasks = task_service.get_overdue_tasks()

            # Assert
            assert len(overdue_tasks) == 1
            assert overdue_tasks[0] == overdue_task
            # Перевіряємо, що викликався метод is_overdue для кожного завдання
            normal_task.is_overdue.assert_called_once()
            overdue_task.is_overdue.assert_called_once()

    def test_get_completed_tasks(self, task_service, sample_task_data):
        """Тест отримання виконаних завдань"""
        # Arrange
        completed_task = task_service.create_task(**sample_task_data)
        task_service.mark_task_done(completed_task.id)

        pending_data = sample_task_data.copy()
        pending_data['title'] = 'Pending Task'
        task_service.create_task(**pending_data)

        # Act
        completed_tasks = task_service.get_completed_tasks()

        # Assert
        assert len(completed_tasks) == 1
        assert completed_tasks[0].id == completed_task.id

    def test_get_pending_tasks(self, task_service, sample_task_data):
        """Тест отримання незавершених завдань"""
        # Arrange
        pending_task = task_service.create_task(**sample_task_data)

        completed_data = sample_task_data.copy()
        completed_data['title'] = 'Completed Task'
        completed_task = task_service.create_task(**completed_data)
        task_service.mark_task_done(completed_task.id)

        # Act
        pending_tasks = task_service.get_pending_tasks()

        # Assert
        assert len(pending_tasks) == 1
        assert pending_tasks[0].id == pending_task.id


class TestMemberService:
    """Тести для MemberService"""

    def test_create_member_success(self, member_service, sample_member_data):
        """Тест успішного створення члена команди"""
        # Arrange
        name = sample_member_data['name']
        role = sample_member_data['role']

        # Act
        member = member_service.create_member(name, role)

        # Assert
        assert member.name == name
        assert member.role == role
        assert member.task_ids == []

    def test_create_member_duplicate_name_raises_error(self, member_service, sample_member_data):
        """Тест створення члена команди з дубльованим іменем"""
        # Arrange
        member_service.create_member(**sample_member_data)

        # Act & Assert
        with pytest.raises(DuplicateMemberError):
            member_service.create_member(**sample_member_data)

    def test_get_member_success(self, member_service, sample_member_data):
        """Тест успішного отримання члена команди за ID"""
        # Arrange
        created_member = member_service.create_member(**sample_member_data)

        # Act
        retrieved_member = member_service.get_member(created_member.id)

        # Assert
        assert retrieved_member.id == created_member.id
        assert retrieved_member.name == created_member.name

    def test_get_nonexistent_member_raises_error(self, member_service):
        """Тест отримання неіснуючого члена команди"""
        # Arrange
        non_existent_id = "non-existent-id"

        # Act & Assert
        with pytest.raises(MemberNotFoundError):
            member_service.get_member(non_existent_id)

    def test_get_all_members(self, member_service, sample_member_data):
        """Тест отримання всіх членів команди"""
        # Arrange
        member1 = member_service.create_member(**sample_member_data)
        member2_data = sample_member_data.copy()
        member2_data['name'] = 'Jane Smith'
        member2 = member_service.create_member(**member2_data)

        # Act
        all_members = member_service.get_all_members()

        # Assert
        assert len(all_members) == 2
        member_ids = [member.id for member in all_members]
        assert member1.id in member_ids
        assert member2.id in member_ids

    def test_update_member_success(self, member_service, sample_member_data):
        """Тест успішного оновлення члена команди"""
        # Arrange
        member = member_service.create_member(**sample_member_data)
        new_name = "Updated Name"
        new_role = "Менеджер"

        # Act
        member_service.update_member(member.id, new_name, new_role)

        # Assert
        updated_member = member_service.get_member(member.id)
        assert updated_member.name == new_name
        assert updated_member.role == new_role

    def test_delete_member(self, member_service, sample_member_data):
        """Тест видалення члена команди"""
        # Arrange
        member = member_service.create_member(**sample_member_data)

        # Act
        member_service.delete_member(member.id)

        # Assert
        with pytest.raises(MemberNotFoundError):
            member_service.get_member(member.id)

    def test_get_member_workload(self, member_service, task_service, sample_member_data, sample_task_data):
        """Тест отримання навантаження члена команди"""
        # Arrange
        member = member_service.create_member(**sample_member_data)
        task_service.create_task(
            title=sample_task_data['title'],
            description=sample_task_data['description'],
            deadline=sample_task_data['deadline'],
            assignee_id=member.id
        )

        # Act
        workload = member_service.get_member_workload(member.id)

        # Assert
        assert workload == 1


class TestProjectManager:
    """Тести для ProjectManager"""

    def test_get_project_progress_no_tasks(self, project_manager):
        """Тест отримання прогресу проекту без завдань"""
        # Act
        progress = project_manager.get_project_progress()

        # Assert
        assert progress == 0.0

    def test_get_project_progress_with_tasks(self, project_manager, sample_task_data):
        """Тест отримання прогресу проекту з завданнями"""
        # Arrange
        # Створюємо 2 завдання, одне виконане
        task1 = project_manager.add_task(**sample_task_data)
        task2_data = sample_task_data.copy()
        task2_data['title'] = 'Completed Task'
        task2 = project_manager.add_task(**task2_data)
        project_manager.mark_task_done(task2.id)

        # Act
        progress = project_manager.get_project_progress()

        # Assert
        assert progress == 50.0  # 1 з 2 завдань виконано

    def test_find_member_by_name(self, project_manager, sample_member_data):
        """Тест пошуку члена команди за іменем"""
        # Arrange
        member = project_manager.add_member(**sample_member_data)

        # Act
        found_member = project_manager.find_member_by_name(sample_member_data['name'])

        # Assert
        assert found_member is not None
        assert found_member.id == member.id
        assert found_member.name == sample_member_data['name']

    def test_find_member_by_name_not_found(self, project_manager):
        """Тест пошуку неіснуючого члена команди за іменем"""
        # Act
        found_member = project_manager.find_member_by_name("Non Existent")

        # Assert
        assert found_member is None