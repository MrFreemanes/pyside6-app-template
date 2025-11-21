import queue
import multiprocessing as mp
import logging
import time
from logging import config
from abc import ABC
from typing import Callable, Any

from config.config import Status, Task, Result
from logs.logger_cfg import cfg


class BaseWorker(ABC):
    """
    Класс-воркер. В наследнике реализуются методы с CPU-GPU-IO нагрузкой.
    Использование (можно несколько процессов, но с уточнением типа в Task):
    worker = Worker(q, q)
    w = mp.Process(target=worker.run, daemon=True)
    w.start()
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._task_map: dict[str, Callable] = {}  # {"название задачи": выполняемая функция}

        # Собрать все методы, помеченные декоратором
        for attr_name, attr in cls.__dict__.items():
            if hasattr(attr, "__task_name__"):
                cls._task_map[attr.__task_name__] = attr

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
        Добавляет методу атрибут __task_name__ для создания __task_map для конкретной реализации класса.
        Применение: оборачивать метод, который будет вызываться
        через bridge.send_task(Task(task_name=NAME_METHOD, ...)).
        :param name: Task.task_name - имя по которому будет выполняться задача.
        :return: Возвращает тот же метод, добавив ему атрибут __task_name__
        """

        def wrapper(method: Callable):
            method.__task_name__ = name
            return method

        return wrapper

    def run(self) -> None:
        """
        Основной цикл worker-процесса. Работает пока не получит None.
        w = mp.Process(target=worker.run, daemon=True)
        w.start()
        """
        while True:
            try:
                self.item: Task = self.task_q.get(timeout=1)  # таймаут в секундах

                if self.item is None: break
                if not self._can_handle():
                    self.task_q.put(self.item)
                    time.sleep(0.01)
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
        Автоматически вызывает метод по имени в классе наследнике,
        если он был добавлен через register_task('имя задачи').
        :param task_name: Имя задачи(название метода).
        """
        handler = self._task_map.get(task_name)
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

    def send_result(self, result: Any, status: str, progress: int, *, text_error: str | None = None) -> None:
        self.result_q.put(
            Result(result=result,
                   result_name=self.item.task_name,
                   result_type=self.__class__.__name__,
                   status=status,
                   progress=progress,
                   text_error=text_error)
        )
