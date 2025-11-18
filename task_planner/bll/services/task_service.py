from typing import List, Optional
from datetime import date
from task_planner.dal.repositories.irepository import IRepository
from task_planner.bll.models.task import Task
from task_planner.bll.exceptions import TaskNotFoundError, DuplicateTaskError, MemberNotFoundError


class TaskService:
    def __init__(self, task_repository: IRepository[Task], member_repository: IRepository):
        self._task_repository = task_repository
        self._member_repository = member_repository

    def create_task(self, title: str, description: str, deadline: date,
                    assignee_id: Optional[str] = None) -> Task:
        """Створює нове завдання"""
        # Перевірка на дублікат
        existing_tasks = self._task_repository.get_all()
        if any(task.title == title for task in existing_tasks):
            raise DuplicateTaskError.by_title(title)

        # Перевірка виконавця
        if assignee_id and not self._member_repository.exists(assignee_id):
            raise MemberNotFoundError.for_task_assignment()

        task = Task(title=title, description=description, deadline=deadline, assignee_id=assignee_id)
        self._task_repository.add(task)

        # Оновлення виконавця
        if assignee_id:
            member = self._member_repository.get_by_id(assignee_id)
            if member:
                member.add_task(task.id)
                self._member_repository.update(member)

        return task

    def get_task(self, task_id: str) -> Task:
        """Отримує завдання за ID"""
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError.by_id()
        return task

    def get_all_tasks(self) -> List[Task]:
        """Отримує всі завдання"""
        return self._task_repository.get_all()

    def update_task_assignee(self, task_id: str, new_assignee_id: Optional[str]) -> None:
        """Оновлює призначеного виконавця для завдання"""
        task = self.get_task(task_id)

        # Видаляємо завдання зі старого виконавця
        if task.assignee_id:
            old_assignee = self._member_repository.get_by_id(task.assignee_id)
            if old_assignee:
                old_assignee.remove_task(task_id)
                self._member_repository.update(old_assignee)

        # Додаємо завдання новому виконавцю
        if new_assignee_id:
            if not self._member_repository.exists(new_assignee_id):
                raise MemberNotFoundError.for_task_assignment()

            new_assignee = self._member_repository.get_by_id(new_assignee_id)
            new_assignee.add_task(task_id)
            self._member_repository.update(new_assignee)

        task.assignee_id = new_assignee_id
        self._task_repository.update(task)

    def mark_task_done(self, task_id: str) -> None:
        """Позначає завдання як виконане"""
        task = self.get_task(task_id)
        task.mark_done()
        self._task_repository.update(task)

    def mark_task_undone(self, task_id: str) -> None:
        """Позначає завдання як невиконане"""
        task = self.get_task(task_id)
        task.mark_undone()
        self._task_repository.update(task)

    def delete_task(self, task_id: str) -> None:
        """Видаляє завдання"""
        task = self.get_task(task_id)

        # Видаляємо завдання з виконавця
        if task.assignee_id:
            assignee = self._member_repository.get_by_id(task.assignee_id)
            if assignee:
                assignee.remove_task(task_id)
                self._member_repository.update(assignee)

        self._task_repository.delete(task_id)

    def get_overdue_tasks(self) -> List[Task]:
        """Отримує всі прострочені завдання"""
        return [task for task in self._task_repository.get_all() if task.is_overdue()]

    def get_completed_tasks(self) -> List[Task]:
        """Отримує всі виконані завдання"""
        return [task for task in self._task_repository.get_all() if task.is_completed]

    def get_pending_tasks(self) -> List[Task]:
        """Отримує всі незавершені завдання"""
        return [task for task in self._task_repository.get_all() if not task.is_completed]