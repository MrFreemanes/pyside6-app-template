from typing import Any, Callable
from config.config import Task, TaskType


def get_task_from_parameters(task_name: str, params: Any, *, task_type: str | None,
                             done_handler: Callable | None, progress_handler: Callable | None) -> Task:
    if done_handler is not None and not callable(done_handler):
        raise ValueError("done_handler must be callable or None")
    if progress_handler is not None and not callable(progress_handler):
        raise ValueError("progress_handler must be callable or None")

    task_kwargs = {
        'task_name': task_name,
        'params': params,
        'progress_handler': progress_handler.__name__ if callable(progress_handler) else None,
        'done_handler': done_handler.__name__ if callable(done_handler) else None
    }

    if task_type:
        task_kwargs['task_type'] = task_type

    return Task(**task_kwargs)
