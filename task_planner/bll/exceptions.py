class TaskError(Exception):
    """Base class for task-related errors"""
    pass


class MemberError(Exception):
    """Base class for team member-related errors"""
    pass


class ValidationError(Exception):
    """Base class for validation errors"""
    pass


class TaskValidationError(ValidationError):
    """Task-specific validation errors"""

    @classmethod
    def empty_title(cls):
        return cls("Назва завдання не може бути порожньою")

    @classmethod
    def past_deadline(cls):
        return cls("Дедлайн не може бути в минулому")


class MemberValidationError(ValidationError):
    """Team member-specific validation errors"""

    @classmethod
    def empty_name(cls):
        return cls("Ім'я члена команди не може бути порожнім")

    @classmethod
    def empty_role(cls):
        return cls("Роль члена команди не може бути порожньою")


class DuplicateError(Exception):
    """Base class for duplicate entry errors"""
    pass


class DuplicateMemberError(DuplicateError):
    """Error for duplicate team members"""

    @classmethod
    def by_name(cls, name: str):
        return cls(f"Член команди з іменем '{name}' вже існує")


class DuplicateTaskError(DuplicateError):
    """Error for duplicate tasks"""

    @classmethod
    def by_title(cls, title: str):
        return cls(f"Завдання з назвою '{title}' вже існує")


class NotFoundError(Exception):
    """Base class for not found errors"""
    pass


class MemberNotFoundError(NotFoundError):
    """Error when team member is not found"""

    @classmethod
    def by_id(cls):
        return cls("Член команди не знайдений")

    @classmethod
    def for_task_assignment(cls):
        return cls("Призначений член команди не знайдений")


class TaskNotFoundError(NotFoundError):
    """Error when task is not found"""

    @classmethod
    def by_id(cls):
        return cls("Завдання не знайдене")