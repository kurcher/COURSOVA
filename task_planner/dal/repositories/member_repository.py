import json
import os
from typing import List, Optional
from task_planner.bll.models.team_member import TeamMember
from .irepository import IRepository


class MemberRepository(IRepository[TeamMember]):
    def __init__(self, data_file: str = "data/data.json"):
        self.data_file = data_file
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self):
        """Створює файл даних, якщо він не існує"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({"tasks": [], "members": []}, f, ensure_ascii=False, indent=2)

    def get_by_id(self, id: str) -> Optional[TeamMember]:
        members = self.get_all()
        return next((member for member in members if member.id == id), None)

    def get_all(self) -> List[TeamMember]:
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [TeamMember.from_dict(member_data) for member_data in data.get('members', [])]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def add(self, member: TeamMember) -> None:
        members = self.get_all()
        members.append(member)
        self._save_all(members)

    def update(self, member: TeamMember) -> None:
        members = self.get_all()
        for i, existing_member in enumerate(members):
            if existing_member.id == member.id:
                members[i] = member
                break
        self._save_all(members)

    def delete(self, id: str) -> None:
        members = [member for member in self.get_all() if member.id != id]
        self._save_all(members)

    def exists(self, id: str) -> bool:
        return self.get_by_id(id) is not None

    def _save_all(self, members: List[TeamMember]) -> None:
        """Зберігає всіх членів команди у файл"""
        try:
            # Спочатку завантажуємо поточні дані
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Оновлюємо тільки членів команди
            data['members'] = [member.to_dict() for member in members]

            # Зберігаємо оновлені дані
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            raise RuntimeError(f"Помилка збереження членів команди: {str(e)}")