import logging
from abc import abstractmethod
from logging import config

from PySide6.QtWidgets import QMainWindow, QApplication

from gui.dialogs.error_dialog import ErrorDialog
from core.bridges.base_bridge import BaseBridge
from logs.logger_cfg import cfg


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

        self.bridge.error_signal.connect(self._dialog_error)
        self._connect_bridge_signals()

        self._setup_ui()
        self._connect_widget()

    @abstractmethod
    def _connect_bridge_signals(self) -> None:
        """Базовое подключение сигналов моста"""
        pass

    @abstractmethod
    def _setup_ui(self) -> None:
        """Создание и настройка UI. (реализуется в наследнике)"""
        pass

    @abstractmethod
    def _connect_widget(self) -> None:
        """Подключение сигналов UI. (реализуется в наследнике)"""
        pass

    def _dialog_error(self, message: str) -> None:
        """
        Подключается к сигналу который уведомляет о промежуточных результатах.
        :param message: Сообщение, которое будет показано пользователю.
        """
        QApplication.beep()
        self.logger.error('Получен сигнал об ошибке от Bridge: %s', message)
        dialog = ErrorDialog(message)
        dialog.exec()  # модальное окно
