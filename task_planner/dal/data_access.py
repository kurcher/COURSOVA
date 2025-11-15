import json
import os
from typing import Dict, List, Any
from datetime import datetime


class DataAccessLayer:
    def __init__(self, data_file: str = "data/data.json"):
        self.data_file = data_file
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self):
        """Створює файл даних, якщо він не існує"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({"members": [], "tasks": []}, f, ensure_ascii=False, indent=2)

    def load_members(self) -> List[Dict[str, Any]]:
        """Завантажує список членів команди з JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('members', [])
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Помилка завантаження членів команди: {e}")
            return []

    def save_members(self, members: List[Dict[str, Any]]) -> None:
        """Зберігає список членів команди в JSON"""
        try:
            # Спочатку завантажуємо поточні дані
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Оновлюємо тільки членів команди
            data['members'] = members

            # Зберігаємо оновлені дані
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Помилка збереження членів команди: {e}")
            raise

    def load_tasks(self) -> List[Dict[str, Any]]:
        """Завантажує список завдань з JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('tasks', [])
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Помилка завантаження завдань: {e}")
            return []

    def save_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        """Зберігає список завдань в JSON"""
        try:
            # Спочатку завантажуємо поточні дані
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Оновлюємо тільки завдання
            data['tasks'] = tasks

            # Зберігаємо оновлені дані
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Помилка збереження завдань: {e}")
            raise