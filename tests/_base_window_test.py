from unittest import TestCase, main
from unittest.mock import Mock, patch

from config.config import Result, Status
from gui.base_window import BaseWindow


class BaseWindowTest(TestCase):
    def test_result_came(self):
        result_came = BaseWindow._result_came

        self_mock = Mock()
        self_mock.call_done = Mock()
        self_mock.call_run = Mock()

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
