from core.bridges.base_bridge import BaseBridge
from config.config import Result, Status


class Bridge(BaseBridge):
    """
    Класс-мост между UI и воркерами.
    Работает в UI-потоке через multiprocessing.Queue и Qt-сигналы.
    Проверяет очередь результатов с интервалом "self.interval".
    Отправляет результат через Signal.emit(result).
    """

    def _handle_result(self, result: Result) -> None:
        """Передача сигнала при получении результата."""
        match result.status:
            case Status.RUN:
                self.result_signal.emit(result)
            case Status.DONE:
                self.result_signal.emit(result)
                self.logger.debug('Получены последние данные')
            case Status.ERROR:
                self.error_signal.emit(result.text_error)
                self.logger.debug('Получена ошибка: %s', result.text_error)
            case _:
                self.error_signal.emit(f'Статус не определен: {result.status}')
                self.logger.warning('Статус не определен: %s', result.status)
