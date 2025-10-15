from gui.base_window import BaseWindow
from gui.ui.ui_untitled import Ui_MainWindow
from gui.widgets.graphs.graph import Graph


class MainWindow(BaseWindow):
    def _setup_ui(self) -> None:
        """Обозначение главных переменных."""
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Расчет чисел Фибоначчи')
        self.graph = Graph(self.ui.group_box_T1, title='Числа Фибоначчи')

    def _connect_widget(self) -> None:
        """Подключение виджетов к функциям."""
        self.ui.btn_calc_T1.clicked.connect(self._run)

    def _connect_bridge_signals(self) -> None:
        """Подключение сигналов из моста."""
        self.bridge.done_signal.connect(self._done_graph)
        self.bridge.process_signal.connect(self._show_process_graph)

    # --- реализация приложения ---
    def _run(self) -> None:
        """ПРИМЕР.
        Отключает виджеты при начале расчетов.
        Уведомляет мост о полученной задаче.
        """
        self.ui.btn_calc_T1.setEnabled(False)
        self.bridge.send_task(100)

        self.logger.debug('Задача отправлена')

    def _show_process_graph(self, result) -> None:
        """ПРИМЕР.
        Подключается к сигналу который уведомляет о промежуточных результатах.
        Производит действия показывающие прогресс работы.
        :param result: Промежуточный результат вычислений.
        """
        self.ui.progress_bar_T1.setValue(result['progress'])
        self.graph.plot_realtime(*result['data'])

        self.logger.debug('Получено промежуточное значение')

    def _done_graph(self, result) -> None:
        """ПРИМЕР.
        Подключается к сигналу который уведомляет о завершении расчетов.
        Производит действия необходимые при завершении расчетов.
        Снимает блокировку ранее отключенных виджетов.
        :param result: Результат вычислений ().
        """
        self.graph.plot_final(*result['data'])
        self.ui.progress_bar_T1.setValue(100)
        self.ui.btn_calc_T1.setEnabled(True)

        self.logger.debug('Расчет окончен. График постоен')
