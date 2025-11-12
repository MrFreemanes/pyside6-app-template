from dataclasses import dataclass
from typing import Any


class Status:
    """Используется в Bridge и в worker"""
    RUN = 'run'
    DONE = 'done'
    ERROR = 'error'


@dataclass(repr=True)
class Task:
    """Датакласс для передачи задач в worker."""
    task_name: str
    num: int


@dataclass(repr=True)
class Result:
    """
    Датакласс для передачи результата включая ошибки.
    :status: Status.
    """
    result: Any
    status: str
    progress: int
    text_error: str = 'Ошибка'
