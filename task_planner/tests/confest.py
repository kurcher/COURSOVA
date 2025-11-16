import pytest
from datetime import date, timedelta
from task_planner.bll.models import Task, TeamMember
from task_planner.bll.services import ProjectManager


@pytest.fixture
def sample_task():
    """Фікстура для тестового завдання"""
    return Task(
        title="Тестове завдання",
        description="Опис тестового завдання",
        deadline=date.today() + timedelta(days=7)
    )


@pytest.fixture
def sample_member():
    """Фікстура для тестового члена команди"""
    return TeamMember(name="Іван Іванов", role="Розробник")


@pytest.fixture
def project_manager_with_data():
    """Фікстура для ProjectManager з тестовими даними"""
    manager = ProjectManager()

    member = TeamMember(name="Тестовий член", role="Розробник")
    manager.members.append(member)

    task = Task(
        title="Тестове завдання",
        description="Опис",
        deadline=date.today() + timedelta(days=1)
    )
    manager.tasks.append(task)

    return manager, member, task