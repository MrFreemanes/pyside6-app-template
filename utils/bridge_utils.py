from typing import Any, Callable
from config.config import Task, TaskType


def get_task_from_parameters(task_name: str, params: Any, *, task_type: TaskType | None,
                             done_handler: Callable | None, progress_handler: Callable | None,
                             finally_handler: Callable | None) -> Task:
    """
    Получает данные для создания задачи для воркера. Создает задачу из данных в виде класса Task.
    :param task_name: Имя задачи в воркере.
    :param params: Параметры, которые придут в воркер.
    :param task_type: Имя воркера.
    :param done_handler: Метод для конечных действий.
    :param progress_handler: Метод для промежуточных действий.
    :param finally_handler: Метод для выполнения задач в случае ошибочной и безошибочной работы worker.
    :return: Task - готовая задача для отправления в воркер.
    """
    if done_handler is not None and not callable(done_handler):
        raise ValueError("done_handler должен быть методом класса или иметь значение None.")
    if progress_handler is not None and not callable(progress_handler):
        raise ValueError("progress_handler должен быть методом класса или иметь значение None.")
    if finally_handler is not None and not callable(finally_handler):
        raise ValueError("finally_handler должен быть методом класса или иметь значение None.")

    task_kwargs = {
        'task_name': task_name,
        'params': params,
        'progress_handler': progress_handler.__name__ if callable(progress_handler) else None,
        'done_handler': done_handler.__name__ if callable(done_handler) else None,
        'finally_handler': finally_handler.__name__ if callable(finally_handler) else None
    }

    if task_type:
        task_kwargs['task_type'] = task_type

    return Task(**task_kwargs)
