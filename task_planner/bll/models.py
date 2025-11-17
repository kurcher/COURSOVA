from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional
import uuid
from .exceptions import TaskValidationError, MemberValidationError





@dataclass
class TeamMember:
    """Клас члена команди"""
    name: str
    role: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_ids: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Валідація після ініціалізації"""
        if not self.name.strip():
            raise MemberValidationError.empty_name()
        if not self.role.strip():
            raise MemberValidationError.empty_role()

    def add_task(self, task_id: str) -> None:
        """Додає ID завдання до списку завдань члена команди"""
        if task_id not in self.task_ids:
            self.task_ids.append(task_id)

    def remove_task(self, task_id: str) -> None:
        """Видаляє ID завдання зі списку завдань члена команди"""
        if task_id in self.task_ids:
            self.task_ids.remove(task_id)

    def get_workload(self) -> int:
        """Повертає кількість завдань члена команди"""
        return len(self.task_ids)

    def to_dict(self) -> dict:
        """Перетворює об'єкт у словник для серіалізації"""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'task_ids': self.task_ids
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TeamMember':
        """Створює об'єкт зі словника"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data['name'],
            role=data['role'],
            task_ids=data.get('task_ids', [])
        )


@dataclass
class Task:
    """Клас завдання"""
    title: str
    description: str
    deadline: date
    assignee_id: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_completed: bool = False
    created_date: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Валідація після ініціалізації"""
        if not self.title.strip():
            raise TaskValidationError.empty_title()
        if self.deadline < date.today():
            raise TaskValidationError.past_deadline()

    def mark_done(self) -> None:
        """Позначає завдання як виконане"""
        self.is_completed = True

    def mark_undone(self) -> None:
        """Позначає завдання як невиконане"""
        self.is_completed = False

    def is_overdue(self) -> bool:
        """Перевіряє, чи прострочено завдання"""
        return not self.is_completed and self.deadline < date.today()

    def to_dict(self) -> dict:
        """Перетворює об'єкт у словник для серіалізації"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat(),
            'assignee_id': self.assignee_id,
            'is_completed': self.is_completed,
            'created_date': self.created_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Створює об'єкт зі словника"""
        deadline_str = data['deadline']
        if isinstance(deadline_str, str):
            deadline = date.fromisoformat(deadline_str)
        else:
            # Якщо deadline вже об'єкт date
            deadline = deadline_str

        created_date_str = data.get('created_date', datetime.now().isoformat())
        if isinstance(created_date_str, str):
            created_date = datetime.fromisoformat(created_date_str)
        else:
            created_date = created_date_str

        return cls(
            id=data.get('id', str(uuid.uuid4())),
            title=data['title'],
            description=data['description'],
            deadline=deadline,
            assignee_id=data.get('assignee_id'),
            is_completed=data.get('is_completed', False),
            created_date=created_date
        )