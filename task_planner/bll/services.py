from typing import List, Optional
from datetime import date
from .models import Task, TeamMember
from .exceptions import (
    TaskError, MemberError,
    DuplicateMemberError, DuplicateTaskError,
    MemberNotFoundError, TaskNotFoundError
)


class ProjectManager:
    """Клас для управління бізнес-логікою проєкту"""

    def __init__(self):
        self.members: List[TeamMember] = []
        self.tasks: List[Task] = []

    def add_member(self, member: TeamMember) -> None:
        """Додає члена команди"""
        if any(m.name == member.name for m in self.members):
            raise DuplicateMemberError.by_name(member.name)
        self.members.append(member)

    def remove_member(self, member_id: str) -> None:
        """Видаляє члена команди за ID"""
        member = self.find_member_by_id(member_id)
        if not member:
            raise MemberNotFoundError.by_id()

        # Видаляємо завдання, призначені цьому члену команди
        for task in self.tasks[:]:
            if task.assignee_id == member_id:
                self.tasks.remove(task)

        self.members = [m for m in self.members if m.id != member_id]

    def find_member_by_id(self, member_id: str) -> Optional[TeamMember]:
        """Знаходить члена команди за ID"""
        return next((m for m in self.members if m.id == member_id), None)

    def find_member_by_name(self, name: str) -> Optional[TeamMember]:
        """Знаходить члена команди за іменем"""
        return next((m for m in self.members if m.name == name), None)

    def add_task(self, task: Task) -> None:
        """Додає завдання"""
        if any(t.title == task.title for t in self.tasks):
            raise DuplicateTaskError.by_title(task.title)

        if task.assignee_id:
            assignee = self.find_member_by_id(task.assignee_id)
            if not assignee:
                raise MemberNotFoundError.for_task_assignment()
            assignee.add_task(task.id)

        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Видаляє завдання за ID"""
        task = self.find_task_by_id(task_id)
        if not task:
            raise TaskNotFoundError.by_id()

        if task.assignee_id:
            assignee = self.find_member_by_id(task.assignee_id)
            if assignee:
                assignee.remove_task(task_id)

        self.tasks = [t for t in self.tasks if t.id != task_id]

    def find_task_by_id(self, task_id: str) -> Optional[Task]:
        """Знаходить завдання за ID"""
        return next((t for t in self.tasks if t.id == task_id), None)

    def update_task_assignee(self, task_id: str, new_assignee_id: Optional[str]) -> None:
        """Оновлює призначеного виконавця для завдання"""
        task = self.find_task_by_id(task_id)
        if not task:
            raise TaskNotFoundError.by_id()

        # Видаляємо завдання зі старого виконавця
        if task.assignee_id:
            old_assignee = self.find_member_by_id(task.assignee_id)
            if old_assignee:
                old_assignee.remove_task(task_id)

        # Додаємо завдання новому виконавцю
        if new_assignee_id:
            new_assignee = self.find_member_by_id(new_assignee_id)
            if not new_assignee:
                raise MemberNotFoundError.for_task_assignment()
            new_assignee.add_task(task_id)

        task.assignee_id = new_assignee_id

    def get_member_tasks(self, member_id: str) -> List[Task]:
        """Отримує всі завдання члена команди"""
        return [t for t in self.tasks if t.assignee_id == member_id]

    def get_overdue_tasks(self) -> List[Task]:
        """Отримує всі прострочені завдання"""
        return [t for t in self.tasks if t.is_overdue()]

    def get_completed_tasks(self) -> List[Task]:
        """Отримує всі виконані завдання"""
        return [t for t in self.tasks if t.is_completed]

    def get_pending_tasks(self) -> List[Task]:
        """Отримує всі незавершені завдання"""
        return [t for t in self.tasks if not t.is_completed]

    def get_project_progress(self) -> float:
        """Розраховує прогрес проєкту (відсоток виконаних завдань)"""
        if not self.tasks:
            return 0.0
        completed = len(self.get_completed_tasks())
        return (completed / len(self.tasks)) * 100