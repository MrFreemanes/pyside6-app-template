from dataclasses import dataclass
from typing import Any


class Status:
    """Используется в Bridge и в worker"""
    RUN = 'run'
    DONE = 'done'
    ERROR = 'error'


class TaskType:
    """
    Содержит в себе имена дочерних классов от BaseWorker.
    Используется для направления задачи в нужный "Worker".
    """
    WORKER = 'Worker'
    WRITER = 'Writer'


@dataclass(frozen=True)
class Task:
    """
    Датакласс для передачи задач в worker.
    :task_type: TaskType, определяет в какой процесс пойдет задача.
    """
    task_name: str
    num: int
    task_type: str = TaskType.WORKER

    def __post_init__(self):
        if self.task_type not in TaskType.__dict__.values():
            raise ValueError(f"Invalid task_type: {self.task_type}")


@dataclass(frozen=True)
class Result:
    """
    Датакласс для передачи результата вычислений включая ошибки.
    :status: Status.
    """
    result: Any
    status: str
    progress: int
    text_error: str = 'Ошибка'

    def __post_init__(self):
        if self.status not in Status.__dict__.values():
            raise ValueError(f"Invalid status: {self.status}")
