from unittest import TestCase, main
from unittest.mock import Mock, call

from utils.bridge_utils import get_task_from_parameters
from config.config import Task, TaskType


def done_handler():
    pass


def progress_handler():
    pass


def finally_handler():
    pass


class BridgeUtilsTest(TestCase):
    def setUp(self):
        self.task_name = 'Name'
        self.params = 123
        self.task_type = TaskType.WRITER

    def test_get_task_from_parameters(self):
        reference_task = Task(
            task_name=self.task_name,
            params=self.params,
            task_type=self.task_type,
            done_handler='done_handler',
            progress_handler='progress_handler',
            finally_handler='finally_handler'
        )

        task = self.call_get_task_from_bad_parameters(done_handler, progress_handler, finally_handler)

        self.assertEqual(task, reference_task)

    def test_get_task_from_bad_parameters(self):
        with self.assertRaises(ValueError):
            self.call_get_task_from_bad_parameters(done_handler, progress_handler, 'finally_handler')

        with self.assertRaises(ValueError):
            self.call_get_task_from_bad_parameters(done_handler, 'progress_handler', finally_handler)

        with self.assertRaises(ValueError):
            self.call_get_task_from_bad_parameters('done_handler', progress_handler, finally_handler)

    def call_get_task_from_bad_parameters(self, p_done_handler, p_progress_handler, p_finally_handler):
        return get_task_from_parameters(
            self.task_name,
            self.params,
            task_type=self.task_type,
            done_handler=p_done_handler,
            progress_handler=p_progress_handler,
            finally_handler=p_finally_handler
        )
