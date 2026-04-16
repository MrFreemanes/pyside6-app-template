from dataclasses import dataclass
from enum import Enum
from typing import Any

NAME_APP = "MyApp"

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
    progress: int  | None = None

    text_error: str | None = None
    # название методов для вызова в GUI
    progress_handler: str | None = None
    done_handler: str | None = None

    def __post_init__(self):
        if self.progress_handler is not None and not isinstance(self.progress_handler, str):
            raise ValueError(f"Неверный тип progress_handler: {type(self.progress_handler)}")

        if self.done_handler is not None and not isinstance(self.done_handler, str):
            raise ValueError(f"Неверный тип done_handler: {type(self.done_handler)}")

        if self.progress is not None and not isinstance(self.progress, int):
            raise ValueError(f"Неверный тип progress: {type(self.progress)}")

        if self.result is not None and callable(self.result):
            raise ValueError("result не должен быть callable")

        if not isinstance(self.status, Status):
            raise ValueError(f"Неверный тип status: {type(self.status)}")

        if self.status == Status.ERROR and not self.text_error and callable(self.text_error):
            raise ValueError("При status=ERROR необходимо указать текст ошибки с str")