import logging
from abc import abstractmethod
from logging import config

from PySide6.QtWidgets import QMainWindow, QApplication

from gui.dialogs.error_dialog import ErrorDialog
from core.bridges.base_bridge import BaseBridge
from logs.logger_cfg import cfg
from config.config import Result


class BaseWindow(QMainWindow):
    """
    Базовый класс для всех главных окон приложения.
    Обеспечивает:
      - автоматическое подключение логгера
      - базовую обработку ошибок через диалог
      - связку с мостом (bridges)
      - шаблон для настройки интерфейса и сигналов
    """

    def __init__(self, bridge: BaseBridge):
        super().__init__()

        logging.config.dictConfig(cfg)
        self.logger = logging.getLogger('log_gui')
        self.bridge = bridge

        self.callbacks = {}
        self.set_callbacks()

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

    @abstractmethod
    def set_callbacks(self):
        pass

    def _result_came(self, result: Result):
        callback = self.callbacks.get(result.result_type).get(result.result_name).get(result.status)
        if callback is not None:
            callback(result)

    def _dialog_error(self, message: str) -> None:
        """
        Подключается к сигналу который уведомляет о промежуточных результатах.
        :param message: Сообщение, которое будет показано пользователю.
        """
        QApplication.beep()
        self.logger.error('Получен сигнал об ошибке от Bridge: %s', message)
        dialog = ErrorDialog(message)
        dialog.exec()  # модальное окно
