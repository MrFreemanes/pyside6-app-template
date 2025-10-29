import multiprocessing as mp
import time
from functools import lru_cache
from queue import Queue

from config.config import Status, Task, Result


def worker(task_q: mp.Queue, result_q: mp.Queue):
    """
    CPU-GPU-IO нагрузка. Используется как отдельный процесс.
    :param task_q: Очередь с задачами
    :param result_q: Очередь с результатами
    """
    while True:
        item: Task = task_q.get()

        if item is None: break

        task = item.task

        if task == 'calc':
            calculation(result_q, item.num)


def calculation(result_q: Queue, number: int) -> None:
    """
    Тут может быть что угодно создающее нагрузку.
    :param result_q:
    :param number:
    """
    check_list = {1, 2}

    @lru_cache(maxsize=32)
    def calc(num):
        if num in (1, 2):
            return 1
        res = calc(num - 1) + calc(num - 2)
        if num not in check_list:
            result_q.put(Result(result=(num, res), status=Status.RUN, progress=int(num / number * 100), ))
            check_list.add(num)
            time.sleep(0.05)  # видимость нагрузки
        return res

    result = calc(number)

    result_q.put(Result(result=(number, result), status=Status.DONE, progress=100, ))
