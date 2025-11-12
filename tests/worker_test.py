from multiprocessing import Queue
from unittest import TestCase, main
from unittest.mock import MagicMock

from config.config import Result, Status, Task
from core.workers.worker import Worker


class WorkerTest(TestCase):
    def setUp(self):
        self.task_q = Queue()
        self.result_q = Queue()
        self.worker = Worker(self.task_q, self.result_q)

        self.worker.logger = MagicMock()

    def test_calc(self):
        self.task_q.put(Task('calc', 3))
        self.task_q.put(None)
        self.worker.run()

        self.assertEqual(self.result_q.get(),
                         Result(result=(3, 2), status=Status.RUN, progress=100, text_error='Ошибка'))

        self.assertEqual(self.result_q.get(),
                         Result(result=(3, 2), status=Status.DONE, progress=100, text_error='Ошибка'))

        self.assertTrue(self.result_q.empty())


if __name__ == '__main__':
    main()
