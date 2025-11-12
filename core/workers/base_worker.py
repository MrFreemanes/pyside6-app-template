import queue
import multiprocessing as mp
import logging
from logging import config
from abc import ABC
from typing import Callable

from config.config import Status, Task, Result
from logs.logger_cfg import cfg


class BaseWorker(ABC):
    """
    Класс-воркер в котором реализуются методы с CPU-GPU-IO нагрузкой.
    Использование:
    worker = Worker(q, q)
    w = mp.Process(target=worker.run, daemon=True)
    w.start()
    """

    task_map: dict[str, Callable] = {}

    def __init__(self, task_q: mp.Queue, result_q: mp.Queue):
        """
        :param task_q: Очередь с задачами
        :param result_q: Очередь с результатами
        """
        logging.config.dictConfig(cfg)
        self.logger = logging.getLogger('log_worker')
        self.logger.debug('Worker инициализирован')

        self._task_q: mp.Queue = task_q
        self._result_q: mp.Queue = result_q
        self.item: Task | None = None

    @classmethod
    def register_task(cls, name: str):
        """
        Добавляет функцию и название для ее вызова в task_map.
        Применение: оборачивать метод, который будет вызываться через bridge.send_task(Task).
        :param name: Task.task
        :return: func
        """

        def wrapper(func):
            cls.task_map[name] = func
            return func

        return wrapper

    def run(self) -> None:
        """
        CPU-GPU-IO нагрузка. Используется как отдельный процесс.
        w = mp.Process(target=worker.run, daemon=True)
        w.start()
        """
        while True:
            try:
                self.item: Task = self._task_q.get(timeout=1)  # таймаут в секундах
                self.logger.debug('Получена задача: %s', self.item)
            except queue.Empty:
                continue

            if self.item is None: break

            self._distributor(self.item.task_name)

    def _distributor(self, task_name: str) -> None:
        """
        Автоматически вызывает метод по имени в классе наследнике, если он был добавлен через register_task.
        :param task_name: Имя задачи.
        """
        handler = self.task_map.get(task_name)
        if not handler:
            self._result_q.put(Result((), Status.ERROR, 100, text_error=f'Неизвестная задача: {task_name}'))
            self.logger.error('Неизвестная задача: %s', task_name)
            return

        try:
            handler(self)
        except Exception as e:
            self._result_q.put(Result((), Status.ERROR, 100,
                                      text_error=f'Ошибка при выполнении задачи {task_name}: {e}'))
            self.logger.exception('Ошибка при выполнении задачи %s', task_name)

    def stop(self) -> None:
        self._task_q.put(None)
        self.logger.debug('Worker остановлен')
