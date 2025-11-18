from datetime import date, datetime
from typing import Optional
from .base_model import BaseModel


class Task(BaseModel):
    """Клас завдання"""

    def __init__(self, title: str, description: str, deadline: date,
                 assignee_id: Optional[str] = None, is_completed: bool = False, **kwargs):
        # Викликаємо конструктор батьківського класу
        super().__init__(**kwargs)

        self.title = title
        self.description = description
        self.deadline = deadline
        self.assignee_id = assignee_id
        self.is_completed = is_completed

        # Валідація
        if not self.title.strip():
            from ..exceptions import TaskValidationError
            raise TaskValidationError.empty_title()
        if self.deadline < date.today():
            from ..exceptions import TaskValidationError
            raise TaskValidationError.past_deadline()

    def mark_done(self) -> None:
        """Позначити завдання як виконане"""
        self.is_completed = True
        self.update_timestamp()

    def mark_undone(self) -> None:
        """Позначити завдання як невиконане"""
        self.is_completed = False
        self.update_timestamp()

    def is_overdue(self) -> bool:
        """Перевірити, чи прострочено завдання"""
        return not self.is_completed and self.deadline < date.today()

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat(),
            'assignee_id': self.assignee_id,
            'is_completed': self.is_completed
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        # Обробка deadline
        deadline_str = data['deadline']
        if isinstance(deadline_str, str):
            deadline = date.fromisoformat(deadline_str)
        else:
            deadline = deadline_str

        # Обробка дат створення та оновлення
        created_date = cls._parse_datetime(data.get('created_date'))
        updated_date = cls._parse_datetime(data.get('updated_date'))

        # Створюємо об'єкт
        task = cls(
            title=data['title'],
            description=data['description'],
            deadline=deadline,
            assignee_id=data.get('assignee_id'),
            is_completed=data.get('is_completed', False),
            id=data.get('id'),
            created_date=created_date,
            updated_date=updated_date
        )

        return task

    @staticmethod
    def _parse_datetime(datetime_str):
        """Парсить datetime з рядка або повертає поточний"""
        if datetime_str and isinstance(datetime_str, str):
            return datetime.fromisoformat(datetime_str)
        return datetime.now()

    def __repr__(self):
        return f"Task(id='{self.id}', title='{self.title}', deadline={self.deadline})"