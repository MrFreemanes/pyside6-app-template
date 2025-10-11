import multiprocessing as mp
from PySide6.QtCore import QObject, Signal, QTimer


class BaseBridge(QObject):
    """
    Класс-мост между UI и воркерами.
    Работает через multiprocessing.Queue и Qt-сигналы.
    """

    # --- Сигналы ---
    error_signal = Signal(str)  # Ошибка воркера
    process_signal = Signal(dict)  # Прогресс/статус задачи
    done_signal = Signal(dict)  # Завершённый результат

    def __init__(self, task_q: mp.Queue, result_q: mp.Queue, interval: int = 200):
        """
        :param task_q: Очередь задач для воркеров
        :param result_q: Очередь результатов от воркеров
        :param interval: Интервал проверки очереди (мс)
        """
        super().__init__()

        self.task_q = task_q
        self.result_q = result_q
        self.interval = interval

        # Таймер для регулярной проверки результатов
        self._timer = QTimer()
        self._timer.timeout.connect(self.check_result)
        self._timer.start(100)

    def send_task(self, params) -> None:
        """Отправить задачу в очередь (с безопасной проверкой)."""
        try:
            if self.task_q.full():
                self.error_signal.emit("Очередь задач переполнена — воркер занят.")
            else:
                self.task_q.put(params)
        except Exception as e:
            # logger
            self.error_signal.emit(f"Ошибка при отправке задачи: {e}")

    def check_result(self) -> None:
        """Проверить очередь результатов и эмитить нужный сигнал."""
        try:
            while not self.result_q.empty():
                result = self.result_q.get_nowait()
                self._handle_result(result)
        except Exception as e:
            # logger
            self.error_signal.emit(f"Ошибка при получении результата: {e}")

    def _handle_result(self, result):
        """Обработка полученного результата (реализуется в наследнике)."""
        raise NotImplementedError(f"{self.__class__.__name__}._handle_result() не реализован")


t = BaseBridge(mp.Queue(), mp.Queue())
