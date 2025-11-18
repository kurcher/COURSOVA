from datetime import datetime
from typing import List
from .base_model import BaseModel


class TeamMember(BaseModel):
    """Клас члена команди"""

    def __init__(self, name: str, role: str, task_ids: List[str] = None, **kwargs):
        # Викликаємо конструктор батьківського класу
        super().__init__(**kwargs)

        self.name = name
        self.role = role
        self.task_ids = task_ids or []

        # Валідація
        if not self.name.strip():
            from ..exceptions import MemberValidationError
            raise MemberValidationError.empty_name()
        if not self.role.strip():
            from ..exceptions import MemberValidationError
            raise MemberValidationError.empty_role()

    def add_task(self, task_id: str) -> None:
        """Додати ID завдання до списку завдань члена команди"""
        if task_id not in self.task_ids:
            self.task_ids.append(task_id)
            self.update_timestamp()

    def remove_task(self, task_id: str) -> None:
        """Видалити ID завдання зі списку завдань члена команди"""
        if task_id in self.task_ids:
            self.task_ids.remove(task_id)
            self.update_timestamp()

    def get_workload(self) -> int:
        """Повертає кількість завдань члена команди"""
        return len(self.task_ids)

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'role': self.role,
            'task_ids': self.task_ids
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: dict) -> 'TeamMember':
        # Обробка дат
        created_date = cls._parse_datetime(data.get('created_date'))
        updated_date = cls._parse_datetime(data.get('updated_date'))

        # Створюємо об'єкт
        member = cls(
            name=data['name'],
            role=data['role'],
            task_ids=data.get('task_ids', []),
            id=data.get('id'),
            created_date=created_date,
            updated_date=updated_date
        )

        return member

    @staticmethod
    def _parse_datetime(datetime_str):
        """Парсить datetime з рядка або повертає поточний"""
        if datetime_str and isinstance(datetime_str, str):
            return datetime.fromisoformat(datetime_str)
        return datetime.now()

    def __repr__(self):
        return f"TeamMember(id='{self.id}', name='{self.name}', role='{self.role}')"