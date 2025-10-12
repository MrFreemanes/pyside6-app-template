import multiprocessing as mp
import logging
from logging import config
from typing import Any

from PySide6.QtCore import QObject, Signal, QTimer

from logs.logger_cfg import cfg


class BaseBridge(QObject):
    """
    Класс-мост между UI и воркерами.
    Работает через multiprocessing.Queue и Qt-сигналы.
    """

    error_signal = Signal(Any)  # Ошибка воркера
    process_signal = Signal(Any)  # Прогресс/статус задачи
    done_signal = Signal(Any)  # Завершённый результат

    def __init__(self, task_q: mp.Queue, result_q: mp.Queue, interval: int = 200):
        """
        :param task_q: Очередь задач для воркеров
        :param result_q: Очередь результатов от воркеров
        :param interval: Интервал проверки очереди (мс)
        """
        super().__init__()

        logging.config.dictConfig(cfg)
        self.logger = logging.getLogger('log_bridge')

        self.task_q = task_q
        self.result_q = result_q
        self.interval = interval

        # Таймер для проверки результатов
        self._timer = QTimer()
        self._timer.timeout.connect(self.check_result)
        self._timer.start(self.interval)

    def send_task(self, params) -> None:
        """Отправить задачу в очередь (с безопасной проверкой)."""
        try:
            if self.task_q.full():
                self.error_signal.emit('Очередь задач переполнена')
                self.logger.warning('Очередь \"task_q\" переполнена')
            else:
                self.task_q.put(params)
                self.logger.debug('Задача отправлена в \"task_q\" с параметром: %s', params)
        except Exception as e:
            self.logger.error('Ошибка при отправке задачи в \"task_q\": %s', e)
            self.error_signal.emit(f'Ошибка при отправке задачи: {e}')

    def check_result(self) -> None:
        """Проверить очередь результатов и эмитить нужный сигнал."""
        try:
            while not self.result_q.empty():
                result = self.result_q.get_nowait()
                self.logger.debug('Получены данные из \"result_q\"')
                self._handle_result(result)
        except Exception as e:
            self.logger.error('Ошибка при получении результата из \"result_q\": %s', e)
            self.error_signal.emit(f'Ошибка при получении результата: {e}')

    def _handle_result(self, result):
        """Обработка полученного результата (реализуется в наследнике)."""
        self.logger.error('_handle_result() не реализован в %s', self.__class__.__name__)
        raise NotImplementedError(f'{self.__class__.__name__}._handle_result() не реализован')
