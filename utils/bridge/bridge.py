import logging
from logging import config
from multiprocessing.queues import Queue

from utils.bridge.base_bridge import BaseBridge


class Bridge(BaseBridge):
    """
    Пример реализации класса BaseBridge.
    """

    def __init__(self, task_q: Queue, result_q: Queue, *, interval: int = 100):
        super().__init__(task_q, result_q, interval)

    def _handle_result(self, result):
        """ПРИМЕР. Передача сигнала в зависимости от результата."""
        stat = result['status']
        if stat == 'run':
            self.process_signal.emit(result)
            self.logger.debug('Получены промежуточные данные')
        elif stat == 'done':
            self.done_signal.emit(result)
            self.logger.debug('Получены последние данные')
        else:
            self.error_signal.emit(f'Статус не определен: {stat}')
            self.logger.warning('Статус не определен: %s', stat)
