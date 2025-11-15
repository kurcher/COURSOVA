import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from PyQt5.QtWidgets import QApplication
from dal.data_access import DataAccessLayer
from bll.services import ProjectManager
from pl.main_window import MainWindow


def main():
    """Головна функція програми"""
    app = QApplication(sys.argv)
    app.setApplicationName("Планувальник завдань")

    # Ініціалізація шару даних та бізнес-логіки
    dal = DataAccessLayer()
    project_manager = ProjectManager()

    # Створення головного вікна
    window = MainWindow(project_manager, dal)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()