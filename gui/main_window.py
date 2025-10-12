from PySide6.QtWidgets import QMainWindow

from gui.ui.ui_untitled import Ui_MainWindow
from gui.dialogs.error_dialog import ErrorDialog
from gui.widgets.graph.graph import Graph


class MainWindow(QMainWindow):
    """
    Главный класс приложения.
    """

    def __init__(self, bridge):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # главные детали
        self.bridge = bridge
        self.graph = Graph(self.ui.group_box_T1, title='Числа Фибоначчи')

        # подключение сигналов
        self.bridge.error_signal.connect(self._show_dialog_error)
        self.bridge.done_signal.connect(self._done_graph)
        self.bridge.process_signal.connect(self._show_process_graph)

        # подключение виджетов 
        self.ui.btn_calc_T1.clicked.connect(self._run)

    @staticmethod
    def _show_dialog_error(message: str) -> None:
        """
        Подключается к сигналу который уведомляет о промежуточных результатах.
        :param message: Сообщение, которое будет показано пользователю.
        """
        dialog = ErrorDialog(message)
        dialog.exec()  # модальное окно

    def _run(self) -> None:
        """ПРИМЕР.
        Отключает виджеты при начале расчетов.
        Уведомляет мост о полученной задаче.
        """
        self.ui.btn_calc_T1.setEnabled(False)
        self.bridge.send_task(100)

    def _show_process_graph(self, result) -> None:
        """ПРИМЕР.
        Подключается к сигналу который уведомляет о промежуточных результатах.
        Производит действия показывающие прогресс работы.
        :param result: Промежуточный результат вычислений.
        """
        self.ui.progress_bar_T1.setValue(result['progress'])
        self.graph.plot_realtime(*result['data'])

    def _done_graph(self, result) -> None:
        """ПРИМЕР.
        Подключается к сигналу который уведомляет о завершении расчетов.
        Производит действия необходимые при завершении расчетов.
        Снимает блокировку ранее отключенных виджетов.
        :param result: Результат вычислений ().
        """
        self.ui.progress_bar_T1.setValue(100)
        self.graph.plot_final(*result['data'])
        self.ui.btn_calc_T1.setEnabled(True)
