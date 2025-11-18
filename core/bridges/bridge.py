from core.bridges.base_bridge import BaseBridge
from config.config import Status, Result


class Bridge(BaseBridge):
    """
    Пример реализации класса BaseBridge.
    """

    def _handle_result(self, result: Result) -> None:
        """ПРИМЕР. Передача сигнала в зависимости от статуса результата."""
        match result.status:
            case Status.RUN:
                self.process_signal.emit(result)
            case Status.DONE:
                self.done_signal.emit(result)
                self.logger.debug('Получены последние данные')
            case Status.ERROR:
                self.error_signal.emit(result.text_error)
                self.logger.debug('Получена ошибка: %s', result.text_error)
            case _:
                self.error_signal.emit(f'Статус не определен: {stat}')
                self.logger.warning('Статус не определен: %s', stat)
