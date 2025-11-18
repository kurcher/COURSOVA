from typing import List
from task_planner.bll.services.task_service import TaskService
from task_planner.bll.services.member_service import MemberService
from task_planner.bll.models.task import Task
from task_planner.bll.models.team_member import TeamMember


class ProjectManager:
    def __init__(self, task_service: TaskService, member_service: MemberService):
        self._task_service = task_service
        self._member_service = member_service

    # Делегування до MemberService
    def add_member(self, name: str, role: str) -> TeamMember:
        return self._member_service.create_member(name, role)

    def get_member(self, member_id: str) -> TeamMember:
        return self._member_service.get_member(member_id)

    def get_all_members(self) -> List[TeamMember]:
        return self._member_service.get_all_members()

    def update_member(self, member_id: str, name: str, role: str) -> None:
        self._member_service.update_member(member_id, name, role)

    def delete_member(self, member_id: str) -> None:
        self._member_service.delete_member(member_id)

    def get_member_tasks(self, member_id: str) -> List:
        return self._member_service.get_member_tasks(member_id)

    def get_member_workload(self, member_id: str) -> int:
        return self._member_service.get_member_workload(member_id)

    # Делегування до TaskService
    def add_task(self, title: str, description: str, deadline, assignee_id: None = None) -> Task:
        return self._task_service.create_task(title, description, deadline, assignee_id)

    def get_task(self, task_id: str) -> Task:
        return self._task_service.get_task(task_id)

    def get_all_tasks(self) -> List[Task]:
        return self._task_service.get_all_tasks()

    def update_task_assignee(self, task_id: str, new_assignee_id: None) -> None:
        self._task_service.update_task_assignee(task_id, new_assignee_id)

    def mark_task_done(self, task_id: str) -> None:
        self._task_service.mark_task_done(task_id)

    def mark_task_undone(self, task_id: str) -> None:
        self._task_service.mark_task_undone(task_id)

    def delete_task(self, task_id: str) -> None:
        self._task_service.delete_task(task_id)

    # Комбіновані методи
    def get_project_progress(self) -> float:
        """Розраховує прогрес проекту (відсоток виконаних завдань)"""
        tasks = self._task_service.get_all_tasks()
        if not tasks:
            return 0.0
        completed = len(self._task_service.get_completed_tasks())
        return (completed / len(tasks)) * 100

    def get_overdue_tasks(self) -> List[Task]:
        return self._task_service.get_overdue_tasks()

    def get_completed_tasks(self) -> List[Task]:
        return self._task_service.get_completed_tasks()

    def get_pending_tasks(self) -> List[Task]:
        return self._task_service.get_pending_tasks()

    def find_member_by_id(self, member_id: str) -> TeamMember:
        return self._member_service.get_member(member_id)

    def find_member_by_name(self, name: str) -> TeamMember:
        members = self._member_service.get_all_members()
        return next((m for m in members if m.name == name), None)

    def find_task_by_id(self, task_id: str) -> Task:
        return self._task_service.get_task(task_id)