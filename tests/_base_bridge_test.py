from queue import Queue, Full
from unittest import TestCase, main
from unittest.mock import Mock

from config.config import Result, Status, Task
from core.bridges.base_bridge import BaseBridge


class Bridge(BaseBridge):
    def _handle_result(self, result: Result) -> None:
        pass


class BaseBridgeTest(TestCase):
    def setUp(self):
        self.result_q = Queue(maxsize=2)
        self.task = Task('calc', 100, )
        self.task_kwargs = {
            'task_name': 'calc',
            'params': 100,
        }

    def test_send_task(self):
        send_task = Bridge.send_task
        self_mock = Mock()
        send_task(self_mock, **self.task_kwargs)

        self.assertEqual(self_mock._task_q.put.call_args[0][0], self.task)
        self.assertEqual(
            self_mock.logger.debug.call_args[0],
            ('Задача отправлена в \"task_q\" с аргументами: %s', self.task)
        )

    def test_send_bad_task(self):
        send_task = Bridge.send_task
        bad_task = 'asjf;ashkfhsdf'
        self_mock = Mock()
        send_task(self_mock, bad_task, 123, task_type='asda')

        self.assertEqual(
            self_mock.logger.error.call_args[0][0],
            'Некорректные аргументы: %s для %s',
        )
        self.assertEqual(
            self_mock.error_signal.emit.call_args[0][0],
            f'Некорректные аргументы для {bad_task}'
        )

    def test_send_task_in_full_queue(self):
        send_task = Bridge.send_task
        self_mock = Mock()
        self_mock._task_q.put.side_effect = Full()
        send_task(self_mock, **self.task_kwargs)

        self.assertEqual(
            self_mock.error_signal.emit.call_args[0][0],
            'Очередь задач переполнена'
        )
        self.assertEqual(
            self_mock.logger.warning.call_args[0][0],
            'Очередь \"task_q\" переполнена'
        )

    def test_check_result(self):
        check_result = Bridge._check_result
        result = Result(
            100,
            Status.DONE,
            100,
        )
        self.result_q.put(result)
        self_mock = Mock()
        self_mock._result_q = self.result_q
        check_result(self_mock)

        self.assertEqual(self_mock.logger.debug.call_args[0][0], 'Получены данные из \"result_q\"')
        self.assertEqual(self_mock._handle_result.call_args[0][0], result)

    def test_check_bad_result(self):
        check_result = Bridge._check_result
        result = '123'
        self.result_q.put(result)
        self_mock = Mock()
        self_mock._result_q = self.result_q
        check_result(self_mock)

        self_mock._handle_result.assert_not_called()

        self.assertEqual(
            self_mock.logger.error.call_args[0],
            ('Неверный тип результата: %s', type(result))
        )
        self.assertEqual(
            self_mock.logger.exception.call_args[0][0],
            'Ошибка при получении результата из \"result_q\": %s'
        )
        self.assertEqual(
            self_mock.error_signal.emit.call_args[0][0],
            "Ошибка при получении результата"
        )


if __name__ == '__main__':
    main()
