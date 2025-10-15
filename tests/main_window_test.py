from unittest import TestCase, main
from unittest.mock import Mock, patch

from gui.main_window import MainWindow


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

        setup_ui = MainWindow._setup_ui
        setup_ui(self_mock)

        # init ui in _setup_ui()
        self.assertTrue(ui_main_window_mock.called)
        self.assertTrue(ui_mock.setupUi.called)

    def test_connect_widget(self):
        """Тест зависит от реализации и виджетов приложения."""
        pass

    def test_connect_bridge_signals(self):
        """
        Проверяет connect сигналов.
        При создании приложения заменить
        self.assertTrue(bridge_mock.done_signal.connect.called)
        на проверку коннекта на
        bridge_mock.done_signal.connect.assert_called_with(self_mock.NAME_YOUR_FUNC)
        """
        bridge_mock = Mock()
        bridge_mock.done_signal.connect = Mock()
        bridge_mock.process_signal.connect = Mock()

        self_mock = Mock()
        self_mock.bridge = bridge_mock

        connect_bridge_signals = MainWindow._connect_bridge_signals
        connect_bridge_signals(self_mock)

        self.assertTrue(bridge_mock.done_signal.connect.called)
        self.assertTrue(bridge_mock.process_signal.connect.called)


if __name__ == '__main__':
    main()
