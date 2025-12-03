import multiprocessing as mp
import logging
from logging import config
from abc import abstractmethod
from queue import Full, Empty
from typing import Any, Callable

from PySide6.QtCore import QObject, Signal, QTimer

from logs.logger_cfg import cfg
from config.config import Result, TaskType
from utils.bridge_utils import get_task_from_parameters


class BaseBridge(QObject):
    """
    Класс-мост между UI и воркерами.
    Работает в UI-потоке через multiprocessing.Queue и Qt-сигналы.
    Проверяет очередь результатов с интервалом "self.interval".
    Отправляет результат через Signal.emit(result).
    В наследнике реализуется _handle_result для фильтрации результатов через статус.
    """

    error_signal = Signal(str)
    result_signal = Signal(Result)

    def __init__(self, task_q: mp.Queue, result_q: mp.Queue, *, interval: int = 200):
        """
        :param task_q: Очередь задач для воркеров
        :param result_q: Очередь результатов от воркеров
        :param interval: Интервал проверки очереди (мс)
        """
        super().__init__()

        logging.config.dictConfig(cfg)
        self.logger = logging.getLogger('log_bridge')

        self._task_q = task_q
        self._result_q = result_q
        self._interval = interval

        # Таймер для проверки результатов
        self._timer = QTimer()
        self._timer.timeout.connect(self._check_result)
        self._timer.start(self._interval)

    def send_task(self, task_name: str, params: Any, *, task_type: TaskType = None,
                  done_handler: Callable = None, progress_handler: Callable = None) -> None:
        """Проверяет тип и отправляет задачу в очередь."""
        try:
            task = get_task_from_parameters(task_name=task_name, params=params, task_type=task_type,
                                            done_handler=done_handler, progress_handler=progress_handler)

            self._task_q.put(task, block=False)
            self.logger.debug('Задача отправлена в \"task_q\" с аргументами: %s', task)
        except Full:
            self.error_signal.emit('Очередь задач переполнена')
            self.logger.warning('Очередь \"task_q\" переполнена')
        except ValueError as e:
            self.logger.error('Некорректные аргументы: %s для %s', e, task_name)
            self.error_signal.emit(f'Некорректные аргументы для {task_name}')
        except Exception as e:
            self.logger.exception('Ошибка при отправке задачи в \"task_q\": %s', e)
            self.error_signal.emit(f'Ошибка при отправке задачи')

    def _check_result(self) -> None:
        """Проверить очередь на наличие результата и эмитить нужный сигнал."""
        try:
            while True:
                result = self._result_q.get_nowait()
                self.logger.debug('Получены данные из \"result_q\"')

                if not isinstance(result, Result):
                    self.logger.error('Неверный тип результата: %s', type(result))
                    raise TypeError(f'Неверный тип результата: {type(result)}, а должен быть: Result')

                self._handle_result(result)
        except Empty:
            pass
        except Exception as e:
            self.logger.exception('Ошибка при получении результата из \"result_q\": %s', e)
            self.error_signal.emit(f'Ошибка при получении результата')

    @abstractmethod
    def _handle_result(self, result: Result) -> None:
        """Передача сигнала при получении результата."""
        pass
