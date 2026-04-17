from unittest import TestCase, main
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QWidget

from config.config import Result, Status
from gui.base_window import BaseWindow


class BaseWindowTest(TestCase):
    def setUp(self):
        self.task_name = 'Name'
        self.params = 123
        self.widgets = Mock(spec=QWidget)

    @patch('gui.base_window.isinstance')
    def test_run_task_not_widgets(self, isinstance_mock):
        run_task = BaseWindow.run_task

        self_mock = Mock()
        self_mock.bridge.send_task.return_value = False
        run_task(self_mock, self.task_name, self.params)
        isinstance_mock.assert_not_called()

        self_mock.bridge.send_task.return_value = True
        run_task(self_mock, self.task_name, self.params)
        isinstance_mock.assert_not_called()

    def test_run_task(self):
        run_task = BaseWindow.run_task

        self_mock = Mock()
        self_mock.bridge.send_task.return_value = True
        run_task(self_mock, self.task_name, self.params, widgets_block=self.widgets)
        self.widgets.setEnabled.assert_called_once_with(False)

        widgets_1 = Mock(spec=QWidget)
        widgets_2 = Mock(spec=QWidget)
        run_task(self_mock, self.task_name, self.params, widgets_block=[widgets_1, widgets_2])

        widgets_1.setEnabled.assert_called_once_with(False)
        widgets_2.setEnabled.assert_called_once_with(False)

    def test_run_task_bad_widget(self):
        run_task = BaseWindow.run_task

        self_mock = Mock()
        self_mock.bridge.send_task.return_value = True
        bad_widget = Mock()
        with self.assertRaises(ValueError):
            run_task(self_mock, self.task_name, self.params, widgets_block=bad_widget)

    def test_result_came(self):
        result_came = BaseWindow._result_came

        self_mock = Mock()
        self_mock.call_done = Mock()
        self_mock.call_run = Mock()
        self_mock.call_finally = Mock()

        result_run = Result(
            result=10,
            status=Status.RUN,
            progress=100,
            progress_handler='call_run'
        )
        result_came(self_mock, result_run)
        self_mock.call_run.assert_called_once_with(result_run)

        result_done = Result(
            result=10,
            status=Status.DONE,
            progress=100,
            done_handler='call_done'
        )
        result_came(self_mock, result_done)
        self_mock.call_done.assert_called_once_with(result_done)

        result_finally = Result(
            result=(),
            status=Status.FINALLY,
            finally_handler='call_finally'
        )
        result_came(self_mock, result_finally)
        self_mock.call_finally.assert_called_once()

    def test_result_came_attribute_error(self):
        result_came = BaseWindow._result_came

        self_mock = Mock()
        self_mock.call_done.side_effect = AttributeError()

        result_done = Result(
            result=10,
            status=Status.DONE,
            progress=100,
            done_handler='call_done'
        )
        result_came(self_mock, result_done)
        self.assertEqual(
            self_mock.logger.error.call_args[0][0],
            'Нет метода %s'
        )

    @patch('gui.base_window.QApplication.beep')
    @patch('gui.base_window.ErrorDialog')
    def test_dialog_error(self, error_dialog_mock, beep_mock):
        dialog_error = BaseWindow._dialog_error
        dialog_mock_instance = Mock()
        error_dialog_mock.return_value = dialog_mock_instance

        message = 'ERROR'
        self_mock = Mock()
        dialog_error(self_mock, message)

        beep_mock.assert_called_once()
        error_dialog_mock.assert_called_once_with(message)
        dialog_mock_instance.exec.assert_called_once()


if __name__ == '__main__':
    main()
