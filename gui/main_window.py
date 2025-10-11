from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from gui.ui.ui_untitled import Ui_MainWindow
from gui.dialogs.error_dialog import ErrorDialog
from gui.widgets.graph import Graph


class MainWindow(QMainWindow):
    def __init__(self, bridge):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.bridge = bridge
        self.graph = Graph(self.ui.group_box_T1)

        self.bridge.error_signal.connect(self._show_dialog_error)
        self.bridge.done_signal.connect(self.done_graph)
        self.bridge.process_signal.connect(self.show_process_graph)

        self.ui.btn_calc_T1.clicked.connect(self.start)

    def start(self):
        self.ui.btn_calc_T1.setEnabled(False)
        self.bridge.send_task(100)

    @staticmethod
    def _show_dialog_error(message: str):
        dialog = ErrorDialog(message)
        dialog.exec()  # модальное окно

    def show_process_graph(self, result):
        self.ui.progress_bar_T1.setValue(result['progress'])
        self.graph.plot_realtime(*result['data'])

    def done_graph(self, result):
        self.ui.progress_bar_T1.setValue(100)
        self.graph.plot_final(*result['data'])
        self.ui.btn_calc_T1.setEnabled(True)