from queue import Queue
from unittest import TestCase, main
from unittest.mock import Mock, MagicMock

from config.config import Result, Status
from core.bridges.bridge import Bridge


class BridgeTest(TestCase):
    def setUp(self):
        self.bridge = Bridge(Queue(), Queue())

        self.bridge.logger = MagicMock()
        self.bridge.done_signal = Mock()
        self.bridge.error_signal = Mock()
        self.bridge.process_signal = Mock()

    def test_handle_result(self):
        """Зависит от реализации."""
        res_1 = Result(10, Status.RUN, 10)
        res_2 = Result(100, Status.DONE, 100)
        res_3 = Result(100, Status.ERROR, 100, text_error='ERR')
        res_4 = Result(100, 'asd', 100)

        # test status 'run'
        self.bridge._handle_result(res_1)
        self.assertEqual(self.bridge.process_signal.emit.call_args[0][0], res_1)

        # test status 'done'
        self.bridge._handle_result(res_2)
        self.assertEqual(self.bridge.done_signal.emit.call_args[0][0], res_2)
        self.assertEqual(self.bridge.logger.debug.call_args[0][0], 'Получены последние данные')

        # test status 'error'
        self.bridge._handle_result(res_3)
        self.assertEqual(self.bridge.error_signal.emit.call_args[0][0], res_3.text_error)
        self.assertEqual(self.bridge.logger.debug.call_args[0][0], 'Получена ошибка')

        # test non-existent status
        self.bridge._handle_result(res_4)
        self.assertEqual(self.bridge.error_signal.emit.call_args[0][0], f'Статус не определен: {res_4.status}')
        self.assertEqual(self.bridge.logger.warning.call_args[0], ('Статус не определен: %s', res_4.status))


if __name__ == '__main__':
    main()
