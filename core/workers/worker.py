import multiprocessing as mp
import time
from functools import lru_cache


def worker(task_q: mp.Queue, result_q: mp.Queue):
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
                result_q.put({'status': 'run', 'progress': int(num / item * 100), 'data': (num, res)})
                check_list.add(num)
                time.sleep(0.05)
            return res

        result = calc(item)

        result_q.put({'status': 'done', 'data': (item, result)})
