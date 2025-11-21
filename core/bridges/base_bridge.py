import multiprocessing as mp
import logging
from logging import config
from abc import abstractmethod
from queue import Full, Empty

from PySide6.QtCore import QObject, Signal, QTimer

from logs.logger_cfg import cfg
from config.config import Task, Result, Status


class BaseBridge(QObject):
    """
    Класс-мост между UI и воркерами.
    Работает в UI-потоке через multiprocessing.Queue и Qt-сигналы.
    Проверяет очередь результатов с интервалом "self.interval".
    Отправляет результат через Signal.emit(result).
    """

    error_signal = Signal(Result)
    process_signal = Signal(Result)  # Прогресс/статус задачи
    done_signal = Signal(Result)  # Готовый результат

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

    def send_task(self, params: Task) -> None:
        """Отправить задачу в очередь (с проверкой)."""
        try:
            if not isinstance(params, Task):
                self.logger.error('Неверный тип задачи: %s', type(params))
                raise TypeError(f'Неверный тип задачи: {type(params)}, а должен быть: Task')

            self._task_q.put(params, block=False)
            self.logger.debug('Задача отправлена в \"task_q\" с параметром: %s', params)
        except Full:
            self.error_signal.emit('Очередь задач переполнена')
            self.logger.warning('Очередь \"task_q\" переполнена')
        except Exception as e:
            self.logger.exception('Ошибка при отправке задачи в \"task_q\": %s', e)
            self.error_signal.emit(f'Ошибка при отправке задачи: {e}')

    def _check_result(self) -> None:
        """Проверить очередь результатов и эмитить нужный сигнал."""
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
            self.error_signal.emit(f'Ошибка при получении результата: {e}')

    @abstractmethod
    def _handle_result(self, result: Result) -> None:
        """Обработка полученного результата (реализуется в наследнике)."""
        pass
