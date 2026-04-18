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
    Использование (можно несколько процессов с уточнением типа в Task):
    worker = Worker(q, q)
    worker.start()
    ...
    worker.stop()
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
        :param task_q: Очередь с задачами.
        :param result_q: Очередь с результатами.
        :item: Задача отправленная из MainWindow.
        """
        self.worker = None
        logging.config.dictConfig(cfg)
        self.logger = logging.getLogger(f'log_worker_{self.__class__.__name__}')
        self.logger.debug('%s инициализирован', self.__class__.__name__)

        self.task_q: mp.Queue = task_q
        self.result_q: mp.Queue = result_q
        self.item: Task | None = None

    @classmethod
    def register_task(cls, name: str):
        """
        Добавляет методу атрибут __task_name__ для создания __task_map для конкретной реализации класса.
        Применение: оборачивать метод, который будет вызываться
        через run_task(Task(task_name=name, ...)).
        :param name: Task.task_name - имя по которому будет выполняться задача.
        :return: Возвращает тот же метод, добавив ему атрибут __task_name__
        """

        def wrapper(method: Callable):
            method.__task_name__ = name
            return method

        return wrapper

    def run(self) -> None:
        """
        Основной цикл worker-процесса. Забирает задачи проверяя их тип.
        При неподходящем типе возвращает задачи в очередь.
        """
        while True:
            try:
                self.item: Task = self.task_q.get(timeout=1)  # таймаут в секундах
            except queue.Empty:
                continue

            if self.item is None:
                break
            if not self._can_handle(self.item):
                self.task_q.put(self.item)
                time.sleep(0.01)
                continue

            self.logger.debug('Получена задача: %s', self.item)

            self._distributor(self.item.task_name)

    def start(self, daemon=True):
        """Создает процесс (run) и запускает его."""
        self.worker = mp.Process(target=self.run, daemon=daemon, name=f'{self.__class__.__name__}_process')
        self.worker.start()

    def stop(self) -> None:
        """Останавливает процесс."""
        self.worker.terminate()
        self.worker.join()
        self.logger.debug('%s остановлен', self.__class__.__name__)

    def send_result(self, result: Any, status: Status, progress: int | None = None,
                    *, text_error: str | None = None) -> None:
        """
        Отправляет дополненный Result в очередь.
        :param result: Результат вычислений окончательный/промежуточный.
        :param status: Статус выполнения.
        :param progress: (1-100).
        :param text_error: Указывается только при status==error.
        """
        self.result_q.put(
            Result(result=result,
                   status=status,
                   progress=progress,
                   text_error=text_error,
                   progress_handler=self.item.progress_handler,
                   done_handler=self.item.done_handler,
                   finally_handler=self.item.finally_handler)
        )

    def _distributor(self, task_name: str) -> None:
        """
        Автоматически вызывает метод по имени в классе наследнике,
        если он был добавлен через register_task('имя задачи').
        Кидает при ошибке и нормальном выполнении метода результат с Status.FINALLY
        :param task_name: Имя задачи(название метода).
        """
        handler = self._task_map.get(task_name)
        if not handler:
            self.send_result((), Status.FINALLY)
            self.logger.error('Неизвестная задача: %s', task_name)
            return

        try:
            handler(self)
        except Exception as e:
            self.send_result((), Status.ERROR, text_error='Ошибка при выполнении задачи')
            self.logger.exception('Ошибка при выполнении задачи %s, %s', task_name, e)
        finally:
            self.send_result((), Status.FINALLY)

    def _can_handle(self, item) -> bool:
        """Проверка типа задачи."""
        return item.task_type.value == self.__class__.__name__
