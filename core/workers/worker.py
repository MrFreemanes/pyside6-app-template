import time
from functools import lru_cache

from config.config import Status, Result
from core.workers.base_worker import BaseWorker


class Worker(BaseWorker):
    """
    Пример реализации класса BaseWorker.
    """

    @BaseWorker.register_task('calc')
    def calc(self) -> None:
        """
        Пример метода с CPU нагрузкой.
        :self.item: Task from config/config.py
        """
        number = self.item.num
        check_list = {1, 2}

        @lru_cache(maxsize=32)
        def calc(num):
            if num in (1, 2):
                return 1
            res = calc(num - 1) + calc(num - 2)
            if num not in check_list:
                self.result_q.put(Result(result=(num, res), status=Status.RUN, progress=int(num / number * 100), ))
                check_list.add(num)
                time.sleep(0.05)  # видимость нагрузки
            return res

        result = calc(number)

        self.logger.debug('result: %s', result)
        self.result_q.put(Result(result=(number, result), status=Status.DONE, progress=100, ))
