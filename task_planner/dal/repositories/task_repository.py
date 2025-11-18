import json
import os
from typing import List, Optional
from task_planner.bll.models.task import Task
from .irepository import IRepository


class TaskRepository(IRepository[Task]):
    def __init__(self, data_file: str = "data/data.json"):
        self.data_file = data_file
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self):
        """Створює файл даних, якщо він не існує"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({"tasks": [], "members": []}, f, ensure_ascii=False, indent=2)

    def get_by_id(self, id: str) -> Optional[Task]:
        tasks = self.get_all()
        return next((task for task in tasks if task.id == id), None)

    def get_all(self) -> List[Task]:
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Task.from_dict(task_data) for task_data in data.get('tasks', [])]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def add(self, task: Task) -> None:
        tasks = self.get_all()
        tasks.append(task)
        self._save_all(tasks)

    def update(self, task: Task) -> None:
        tasks = self.get_all()
        for i, existing_task in enumerate(tasks):
            if existing_task.id == task.id:
                tasks[i] = task
                break
        self._save_all(tasks)

    def delete(self, id: str) -> None:
        tasks = [task for task in self.get_all() if task.id != id]
        self._save_all(tasks)

    def exists(self, id: str) -> bool:
        return self.get_by_id(id) is not None

    def _save_all(self, tasks: List[Task]) -> None:
        """Зберігає всі завдання у файл"""
        try:
            # Спочатку завантажуємо поточні дані
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Оновлюємо тільки завдання
            data['tasks'] = [task.to_dict() for task in tasks]

            # Зберігаємо оновлені дані
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            raise RuntimeError(f"Помилка збереження завдань: {str(e)}")