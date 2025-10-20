from queue import Queue
from unittest import TestCase, main
from unittest.mock import Mock

from core.bridges.bridge import Bridge


class BridgeTest(TestCase):
    def setUp(self):
        self.bridge = Bridge(Queue(), Queue())

        self.bridge.logger = Mock()
        self.bridge.done_signal = Mock()
        self.bridge.error_signal = Mock()
        self.bridge.process_signal = Mock()

    def test_handle_result(self):
        """Зависит от реализации."""
        res_1 = {'status': 'run'}
        res_2 = {'status': 'done'}
        res_3 = {'status': 'pass'}
        self.bridge._handle_result(res_1)
        self.bridge._handle_result(res_2)
        self.bridge._handle_result(res_3)

        # test run
        self.assertEqual(self.bridge.process_signal.emit.call_args[0][0],
                         res_1)

        # test done
        self.assertEqual(self.bridge.done_signal.emit.call_args[0][0],
                         res_2)
        self.assertEqual(self.bridge.logger.debug.call_args[0][0],
                         'Получены последние данные')

        # test error
        self.assertEqual(self.bridge.error_signal.emit.call_args[0][0],
                         f"Статус не определен: {res_3['status']}")
        self.assertEqual(self.bridge.logger.warning.call_args[0],
                         ('Статус не определен: %s', 'pass'))


if __name__ == '__main__':
    main()
