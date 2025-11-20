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
        self.assertEqual(self.bridge.logger.debug.call_args[0], ('Получена ошибка: %s', 'ERR'))

        # test non-existent status
        with self.assertRaisesRegex(ValueError, "Invalid status: asd"):
            Result(10, 'asd', 12)


if __name__ == '__main__':
    main()
