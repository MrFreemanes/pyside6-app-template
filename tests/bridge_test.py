from unittest import TestCase, main
from unittest.mock import Mock, call

from config.config import Result, Status
from core.bridges.bridge import Bridge


class BridgeTest(TestCase):
    def test_handle_result(self):
        class BadStatus:
            status = 'asd'

        handle_result = Bridge._handle_result
        result_done = Result(100, Status.DONE, 100)
        result_run = Result(50, Status.RUN, 50)
        result_error = Result((), Status.ERROR, 100, text_error='ERROR')
        result_bad_status = BadStatus()
        self_mock = Mock()

        handle_result(self_mock, result_done)
        handle_result(self_mock, result_run)
        handle_result(self_mock, result_error)
        handle_result(self_mock, result_bad_status)

        self_mock.result_signal.emit.assert_has_calls([call(result_done), call(result_run)])
        self_mock.error_signal.emit.assert_has_calls(
            [
                call(result_error.text_error),
                call(f'Статус не определен: {result_bad_status.status}')
            ]
        )

        self_mock.logger.debug.assert_has_calls(
            [
                call('Получены последние данные'),
                call('Получена ошибка: %s', result_error.text_error),
            ]
        )

        self.assertEqual(
            self_mock.logger.warning.call_args[0],
            ('Статус не определен: %s', result_bad_status.status)
        )


if __name__ == '__main__':
    main()
