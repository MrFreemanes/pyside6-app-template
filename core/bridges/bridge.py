from core.bridges.base_bridge import BaseBridge
from config.config import Status


class Bridge(BaseBridge):
    """
    Пример реализации класса BaseBridge.
    """

    def _handle_result(self, result: dict) -> None:
        """ПРИМЕР. Передача сигнала в зависимости от статуса результата."""
        stat = result['status']
        if stat == Status.RUN:
            self.process_signal.emit(result)
        elif stat == Status.DONE:
            self.done_signal.emit(result)
            self.logger.debug('Получены последние данные')
        else:
            self.error_signal.emit(f'Статус не определен: {stat}')
            self.logger.warning('Статус не определен: %s', stat)
