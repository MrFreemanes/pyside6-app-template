import logging
from logging import config
from abc import abstractmethod
from typing import Any, Callable, Iterable

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget

from gui.dialogs.error_dialog import ErrorDialog
from core.bridges.bridge import Bridge
from logs.logger_cfg import cfg
from config.config import Result, Status, TaskType


class BaseWindow(QMainWindow):
    """
    Базовый класс для всех главных окон приложения.
    Обеспечивает:
      - автоматическое подключение логгера
      - базовую обработку ошибок через диалог
      - связку с мостом (bridges)
      - шаблон для настройки интерфейса и сигналов
    """

    def __init__(self, bridge: Bridge):
        super().__init__()

        logging.config.dictConfig(cfg)
        self.logger = logging.getLogger('log_gui')
        self.bridge = bridge

        self.setup_ui()
        self.connect_widget()

        self.bridge.error_signal.connect(self._dialog_error)
        self.bridge.result_signal.connect(self._result_came)

    @abstractmethod
    def setup_ui(self) -> None:
        """Создание и настройка UI. (реализуется в наследнике)"""
        pass

    @abstractmethod
    def connect_widget(self) -> None:
        """Подключение сигналов UI. (реализуется в наследнике)"""
        pass

    def run_task(self, task_name: str, params: Any, *,
                 task_type: TaskType = None,
                 widgets_block: QWidget | Iterable[QWidget] = None,
                 done_handler: Callable = None,
                 progress_handler: Callable = None,
                 finally_handler: Callable = None) -> None:
        """
        Отправляет параметры для создания задачи в Bridge. Отключает переданные виджеты.
        :param task_name: Имя метода в наследнике BaseWorker.
        :param params: Данные необходимые для работы в методе.
        :param task_type: Имя worker.
        :param widgets_block: Виджет/Виджеты для отключения, должны иметь метод ".setEnabled".
        :param done_handler: Метод для выполнения действия при возврате результата со статусом Status.DONE.
        :param progress_handler: Метод для выполнения промежуточного действия
                                 при возврате результата со статусом Status.RUN.
        :param finally_handler: Метод для выполнения в любом случае.
                                Используется например при отключении кнопок
                                для их включения после завершения работы в worker.
        """
        self.logger.debug('Параметры в bridge отправлены')
        ok = self.bridge.send_task(task_name=task_name, params=params, task_type=task_type, done_handler=done_handler,
                                   progress_handler=progress_handler, finally_handler=finally_handler)

        if not ok or not widgets_block:
            return

        if isinstance(widgets_block, QWidget):
            widgets_block = [widgets_block]
        elif not isinstance(widgets_block, Iterable):
            raise ValueError(
                f"Неверный тип widgets_block: {type(widgets_block)}, должен быть QWidget или Iterable[QWidget]"
            )

        for w in widgets_block:
            w.setEnabled(False)

    @Slot(Result)
    def _result_came(self, result: Result) -> None:
        """
        Автоматически вызывает метод реализованный в классе наследнике
        при получении результата в Bridge.
        :param result: Результат промежуточных/окончательных вычислений.
        """
        method_name = {
            Status.DONE: result.done_handler,
            Status.RUN: result.progress_handler,
            Status.FINALLY: result.finally_handler
        }.get(result.status)

        if method_name:
            try:
                if result.status == Status.FINALLY:
                    getattr(self, method_name)()
                    return
                getattr(self, method_name)(result)
            except AttributeError:
                self.logger.error("Нет метода %s", method_name)

    def _dialog_error(self, message: str) -> None:
        """
        Подключается к сигналу который уведомляет об ошибках.
        :param message: Сообщение, которое будет показано пользователю.
        """
        QApplication.beep()
        self.logger.error('Получен сигнал об ошибке от Bridge: %s', message)
        dialog = ErrorDialog(message)
        dialog.exec()  # модальное окно
