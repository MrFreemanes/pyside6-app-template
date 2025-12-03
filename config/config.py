from dataclasses import dataclass
from enum import Enum
from typing import Any


class Status(Enum):
    """Используется в Bridge и в worker для установки статуса выполнения."""
    RUN = 'run'
    DONE = 'done'
    ERROR = 'error'


class TaskType(Enum):
    """
    Содержит в себе имена дочерних классов от BaseWorker в workers/.
    Используется для направления задачи в нужный "Worker".
    ВАЖНО: имена должны совпадать с названиями классов-наследников BaseWorker.
    """
    WORKER = 'Worker'
    WRITER = 'Writer'


@dataclass(frozen=True)
class Task:
    """
    Датакласс для передачи задач в worker.
    :task_type: TaskType, определяет в какой процесс пойдет задача.
    :progress_handler: Название метода для вызова в момент выполнения задачи.
    :done_handler: Название метода для конечного вызова.
    """
    task_name: str
    params: Any

    task_type: TaskType = TaskType.WORKER
    # название методов для вызова в GUI
    progress_handler: str | None = None
    done_handler: str | None = None

    def __post_init__(self):
        if not isinstance(self.task_type, TaskType):
            raise ValueError(f"Invalid task_type: {self.task_type}")


@dataclass(frozen=True)
class Result:
    """
    Датакласс для передачи результата вычислений включая ошибки.
    Если status == Status.ERROR, то text_error не должен быть пустым.
    :status: Status.
    :progress_handler: Название метода для вызова в момент выполнения задачи.
    :done_handler: Название метода для конечного вызова.
    """
    result: Any
    status: Status
    progress: int

    text_error: str | None = None
    # название методов для вызова в GUI
    progress_handler: str | None = None
    done_handler: str | None = None

    def __post_init__(self):
        if not isinstance(self.status, Status):
            raise ValueError(f"Invalid status: {self.status}")

        if self.status == Status.ERROR and not self.text_error:
            raise ValueError("text_error must be provided when status=ERROR")
