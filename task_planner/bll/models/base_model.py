from abc import ABC
from datetime import datetime
import uuid


class BaseModel(ABC):
    """Базовий клас для всіх моделей"""

    def __init__(self, id: str = None, created_date: datetime = None, updated_date: datetime = None):
        self.id = id or str(uuid.uuid4())
        self.created_date = created_date or datetime.now()
        self.updated_date = updated_date or datetime.now()

    def to_dict(self) -> dict:
        """Серіалізація в словник"""
        return {
            'id': self.id,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BaseModel':
        """Десеріалізація зі словника"""
        raise NotImplementedError("Must be implemented in child classes")

    def update_timestamp(self):
        """Оновлення часу модифікації"""
        self.updated_date = datetime.now()