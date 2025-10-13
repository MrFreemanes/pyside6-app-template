import multiprocessing as mp
import time
from functools import lru_cache

from config.config import Status

def worker(task_q: mp.Queue, result_q: mp.Queue):
    """
    CPU-GPU-IO нагрузка. Используется как отдельный процесс.
    :param task_q: Очередь с задачами
    :param result_q: Очередь с результатами
    """
    while True:
        item = task_q.get()

        if item is None: break

        check_list = {1, 2}

        @lru_cache(maxsize=32)
        def calc(num):
            if num in (1, 2):
                return 1
            res = calc(num - 1) + calc(num - 2)
            if num not in check_list:
                result_q.put({'status': Status.RUN, 'progress': int(num / item * 100), 'data': (num, res)})
                check_list.add(num)
                time.sleep(0.05) # видимость нагрузки
            return res

        result = calc(item)

        result_q.put({'status': Status.DONE, 'data': (item, result)})
