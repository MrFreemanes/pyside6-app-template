from queue import Queue, Full, Empty
from unittest import TestCase, main
from unittest.mock import Mock, MagicMock, call

from config.config import Result, Status, Task, TaskType
from core.bridges.bridge import Bridge


class BridgeTest(TestCase):
    def setUp(self):
        self.result_q = Queue(maxsize=2)
        self.task = Task('calc', 100, )

    def test_send_task(self):
        send_task = Bridge.send_task
        self_mock = Mock()
        send_task(self_mock, self.task)

        self.assertEqual(self_mock._task_q.put.call_args[0][0], self.task)
        self.assertEqual(
            self_mock.logger.debug.call_args[0],
            ('Задача отправлена в \"task_q\" с параметром: %s', self.task)
        )

    def test_send_bad_task(self):
        send_task = Bridge.send_task
        bad_task = 'calc'
        self_mock = Mock()
        send_task(self_mock, bad_task)

        self.assertEqual(
            self_mock.logger.error.call_args[0],
            ('Неверный тип задачи: %s', type(bad_task))
        )
        self.assertEqual(
            self_mock.logger.exception.call_args[0][0],
            'Ошибка при отправке задачи в \"task_q\": %s',
        )
        self.assertEqual(
            self_mock.error_signal.emit.call_args[0][0],
            f"Ошибка при отправке задачи: Неверный тип задачи: {type(bad_task)}, а должен быть: Task"
        )

    def test_send_task_in_full_queue(self):
        send_task = Bridge.send_task
        self_mock = Mock()
        self_mock._task_q.put.side_effect = Full()
        send_task(self_mock, self.task)

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
            f"Ошибка при получении результата: Неверный тип результата: {type(result)}, а должен быть: Result"
        )

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
