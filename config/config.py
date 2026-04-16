from dataclasses import dataclass
from enum import Enum
from typing import Any

from utils.config_utils import check_handler

NAME_APP = "MyApp"


class Status(Enum):
    """
    Используется в Bridge и в worker для установки статуса выполнения.
    FINALLY - служебный статус, не предназначен для использования в пользовательской логике.
    """
    RUN = 'run'
    DONE = 'done'
    ERROR = 'error'
    FINALLY = 'finally'


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
    finally_handler: str | None = None

    def __post_init__(self):
        check_handler(self.progress_handler)
        check_handler(self.done_handler)
        check_handler(self.finally_handler)

        if not isinstance(self.task_name, str):
            raise ValueError(f"Неверный тип task_name: {type(self.task_name)}")

        if self.params is not None and callable(self.params):
            raise ValueError("params не должен быть callable")

        if not isinstance(self.task_type, TaskType):
            raise ValueError(f"Неверный тип task_type: {type(self.task_type)}")


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
    progress: int | None = None

    text_error: str | None = None
    # название методов для вызова в GUI
    progress_handler: str | None = None
    done_handler: str | None = None
    finally_handler: str | None = None

    def __post_init__(self):
        check_handler(self.progress_handler)
        check_handler(self.done_handler)
        check_handler(self.finally_handler)

        if self.progress is not None and not isinstance(self.progress, int):
            raise ValueError(f"Неверный тип progress: {type(self.progress)}")

        if self.result is not None and callable(self.result):
            raise ValueError("result не должен быть callable")

        if not isinstance(self.status, Status):
            raise ValueError(f"Неверный тип status: {type(self.status)}")

        if self.status == Status.ERROR and not isinstance(self.text_error, str):
            raise ValueError("При status=ERROR необходимо указать текст ошибки с str")
