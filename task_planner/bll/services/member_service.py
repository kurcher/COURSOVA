from typing import List
from task_planner.dal.repositories.irepository import IRepository
from task_planner.bll.models.team_member import TeamMember
from task_planner.bll.exceptions import MemberNotFoundError, DuplicateMemberError


class MemberService:
    def __init__(self, member_repository: IRepository[TeamMember], task_repository: IRepository):
        self._member_repository = member_repository
        self._task_repository = task_repository

    def create_member(self, name: str, role: str) -> TeamMember:
        """Створює нового члена команди"""
        existing_members = self._member_repository.get_all()
        if any(member.name == name for member in existing_members):
            raise DuplicateMemberError.by_name(name)

        member = TeamMember(name=name, role=role)
        self._member_repository.add(member)
        return member

    def get_member(self, member_id: str) -> TeamMember:
        """Отримує члена команди за ID"""
        member = self._member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError.by_id()
        return member

    def get_all_members(self) -> List[TeamMember]:
        """Отримує всіх членів команди"""
        return self._member_repository.get_all()

    def update_member(self, member_id: str, name: str, role: str) -> None:
        """Оновлює дані члена команди"""
        member = self.get_member(member_id)

        # Перевірка на дублікат (крім поточного члена)
        existing_members = self._member_repository.get_all()
        if any(m.name == name and m.id != member_id for m in existing_members):
            raise DuplicateMemberError.by_name(name)

        member.name = name
        member.role = role
        member.update_timestamp()
        self._member_repository.update(member)

    def delete_member(self, member_id: str) -> None:
        """Видаляє члена команди"""
        member = self.get_member(member_id)

        # Видаляємо всі завдання цього члена команди
        member_tasks = [task for task in self._task_repository.get_all()
                        if task.assignee_id == member_id]
        for task in member_tasks:
            self._task_repository.delete(task.id)

        self._member_repository.delete(member_id)

    def get_member_tasks(self, member_id: str) -> List:
        """Отримує всі завдання члена команди"""
        member = self.get_member(member_id)
        all_tasks = self._task_repository.get_all()
        return [task for task in all_tasks if task.id in member.task_ids]

    def get_member_workload(self, member_id: str) -> int:
        """Отримує кількість завдань члена команди"""
        member = self.get_member(member_id)
        return member.get_workload()