import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from PyQt5.QtWidgets import QApplication
from dal.repositories.task_repository import TaskRepository
from dal.repositories.member_repository import MemberRepository
from bll.services.task_service import TaskService
from bll.services.member_service import MemberService
from bll.services.project_manager import ProjectManager
from pl.main_window import MainWindow


def main():
    """Головна функція програми"""
    app = QApplication(sys.argv)
    app.setApplicationName("Планувальник завдань")

    # Ініціалізація репозиторіїв
    task_repository = TaskRepository()
    member_repository = MemberRepository()

    # Ініціалізація сервісів
    task_service = TaskService(task_repository, member_repository)
    member_service = MemberService(member_repository, task_repository)

    # Ініціалізація менеджера проекту
    project_manager = ProjectManager(task_service, member_service)

    # Створення головного вікна
    window = MainWindow(project_manager)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()