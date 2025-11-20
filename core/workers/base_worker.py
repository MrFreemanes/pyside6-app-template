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
    Использование (можно несколько, но с уточнением типа в Task):
    worker = Worker(q, q)
    w = mp.Process(target=worker.run, daemon=True)
    w.start()
    """

    __task_map: dict[str, Callable] = {}

    def __init__(self, task_q: mp.Queue, result_q: mp.Queue):
        """
        :param task_q: Очередь с задачами
        :param result_q: Очередь с результатами
        """
        logging.config.dictConfig(cfg)
        self.logger = logging.getLogger('log_worker')
        self.logger.debug('%s инициализирован', self.__class__.__name__)

        self.task_q: mp.Queue = task_q
        self.result_q: mp.Queue = result_q
        self.item: Task | None = None

    @classmethod
    def register_task(cls, name: str):
        """
        Добавляет функцию и название для ее вызова в __task_map.
        Применение: оборачивать метод,
        который будет вызываться через bridge.send_task(Task(name_task=NAME_FUNC)).
        :param name: Task.task
        :return: func
        """

        def wrapper(func):
            cls.__task_map[name] = func
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
                self.item: Task = self.task_q.get(timeout=1)  # таймаут в секундах

                if self.item is None: break
                if not self._can_handle():
                    self.task_q.put(self.item)
                    continue

                self.logger.debug('Получена задача: %s', self.item)
            except queue.Empty:
                continue

            self._distributor(self.item.task_name)

    def stop(self) -> None:
        """Останавливает Worker."""
        self.task_q.put(None)
        self.logger.debug('%s остановлен', self.__class__.__name__)

    def _distributor(self, task_name: str) -> None:
        """
        Автоматически вызывает метод по имени в классе наследнике, если он был добавлен через register_task.
        :param task_name: Имя задачи(название функции).
        """
        handler = self.__task_map.get(task_name)
        if not handler:
            self.result_q.put(Result((), Status.ERROR, 100, text_error=f'Неизвестная задача: {task_name}'))
            self.logger.error('Неизвестная задача: %s', task_name)
            return

        try:
            handler(self)
        except Exception as e:
            self.result_q.put(Result((), Status.ERROR, 100,
                                     text_error=f'Ошибка при выполнении задачи {task_name}: {e}'))
            self.logger.exception('Ошибка при выполнении задачи %s', task_name)

    def _can_handle(self) -> bool:
        """Проверка типа задачи."""
        return self.item.task_type == self.__class__.__name__
