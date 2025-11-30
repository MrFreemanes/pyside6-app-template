from enum import Enum
from queue import Queue
from unittest import TestCase, main
from unittest.mock import MagicMock, Mock

from config.config import Result, Status, Task
from core.workers.base_worker import BaseWorker

NAME_FUNC = 'put_back'


class TestWorker(BaseWorker):
    @BaseWorker.register_task(NAME_FUNC)
    def put_back(self):
        self.send_result(self.item.params, Status.DONE, 100)


class TestTask(Task):
    def __post_init__(self):
        pass


class TaskType(Enum):
    TEST_WORKER = 'TestWorker'


class BaseWorkerTest(TestCase):
    def setUp(self):
        self.task_q = Queue()
        self.result_q = Queue()
        self.worker = TestWorker(self.task_q, self.result_q)

        self.worker.logger = MagicMock()

    def test_task_map(self):
        self.assertIn(NAME_FUNC, self.worker._task_map)

    def test_run(self):
        self.task_q.put(
            TestTask(task_name=NAME_FUNC,
                     params=10,
                     done_handler='done_handler',
                     progress_handler='progress_handler',
                     task_type=TaskType.TEST_WORKER)
        )
        self.task_q.put(None)
        self.worker.run()

        self.assertEqual(
            self.result_q.get(),
            Result(result=10,
                   status=Status.DONE,
                   progress=100,
                   text_error=None,
                   progress_handler='progress_handler',
                   done_handler='done_handler')

        )

    def test_register_task(self):
        class TempWorker(BaseWorker):
            @BaseWorker.register_task('hello')
            def hello(self):
                pass

        self.assertIn('hello', TempWorker._task_map)

    def test_distributor(self):
        distributor = TestWorker._distributor
        self_mock = Mock()
        handler_func_mock = MagicMock()
        self_mock._task_map = {NAME_FUNC: handler_func_mock}
        distributor(self_mock, NAME_FUNC)

        handler_func_mock.assert_called_once()

    def test_distributor_for_an_undefined_name(self):
        distributor = TestWorker._distributor
        self_mock = Mock()
        self_mock.result_q = Mock()
        self_mock.logger = Mock()
        self_mock._task_map = {}
        distributor(self_mock, NAME_FUNC)

        self.assertEqual(
            self_mock.result_q.put.call_args[0][0],
            Result((), Status.ERROR, 100, text_error=f'Неизвестная задача: {NAME_FUNC}')
        )
        self.assertEqual(
            self_mock.logger.error.call_args[0],
            ('Неизвестная задача: %s', NAME_FUNC)
        )


if __name__ == '__main__':
    main()
