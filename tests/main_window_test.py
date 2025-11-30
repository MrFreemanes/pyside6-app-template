from unittest import TestCase, main
from unittest.mock import Mock, patch

from gui.main_window import MainWindow
from config.config import Task


class MainWindowTest(TestCase):
    """
    Тест класса MainWindow. Минимальный пример реализации тестов.
    Проверка инициализации ui через Ui_MainWindow.
    Проверка привязки сигналов из класса Bridge.
    """

    @patch('gui.main_window.Graph', create=True)
    @patch('gui.main_window.Ui_MainWindow')
    def test_setup_ui(self, ui_main_window_mock, graph_mock):
        """
        Тест не полный. Проверяет, был ли создан ui.
        Остальные проверки зависят от конкретной реализации.
        """
        ui_mock = Mock()
        ui_mock.setupUi = Mock(return_value=None)

        ui_main_window_mock.return_value = ui_mock
        graph_mock.return_value = Mock()

        self_mock = Mock()

        setup_ui = MainWindow.setup_ui
        setup_ui(self_mock)

        # init ui in _setup_ui()
        self.assertTrue(ui_main_window_mock.called)
        self.assertTrue(ui_mock.setupUi.called)

    def test_run(self):
        run = MainWindow._run
        self_mock = Mock()
        run(self_mock)

        self.assertFalse(self_mock.ui.btn_calc_T1.setEnabled.call_args[0][0])
        self_mock.bridge.send_task.assert_called_once_with(
            'calc',
            {'num': 100},
            done_handler=self_mock._done_graph,
            progress_handler=self_mock._show_process_graph
        )


if __name__ == '__main__':
    main()
