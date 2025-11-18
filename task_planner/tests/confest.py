import pytest
from datetime import date, datetime, timedelta
from task_planner.bll.models.task import Task
from task_planner.bll.models.team_member import TeamMember
from task_planner.dal.repositories.task_repository import TaskRepository
from task_planner.dal.repositories.member_repository import MemberRepository
from task_planner.bll.services.task_service import TaskService
from task_planner.bll.services.member_service import MemberService
from task_planner.bll.services.project_manager import ProjectManager
import os
import tempfile
import json


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
    """Фікстура з даними для тестового завдання"""
    return {
        'title': 'Test Task',
        'description': 'Test Description',
        'deadline': date.today() + timedelta(days=7)
    }


@pytest.fixture
def sample_member_data():
    """Фікстура з даними для тестового члена команди"""
    return {
        'name': 'John Doe',
        'role': 'Розробник'
    }


@pytest.fixture
def task_repository(temp_data_file):
    """Фікстура репозиторію завдань"""
    return TaskRepository(temp_data_file)


@pytest.fixture
def member_repository(temp_data_file):
    """Фікстура репозиторію членів команди"""
    return MemberRepository(temp_data_file)


@pytest.fixture
def task_service(task_repository, member_repository):
    """Фікстура сервісу завдань"""
    return TaskService(task_repository, member_repository)


@pytest.fixture
def member_service(member_repository, task_repository):
    """Фікстура сервісу членів команди"""
    return MemberService(member_repository, task_repository)


@pytest.fixture
def project_manager(task_service, member_service):
    """Фікстура ProjectManager"""
    return ProjectManager(task_service, member_service)