from multiprocessing.queues import Queue

from utils.base_bridge import BaseBridge


class Bridge(BaseBridge):
    def __init__(self, task_q: Queue, result_q: Queue, *, interval: int = 200):
        super().__init__(task_q, result_q, interval)

    def _handle_result(self, result):
        stat = result['status']
        if stat == 'run':
            self.process_signal.emit(result)
        elif stat == 'done':
            self.done_signal.emit(result)
        else:
            self.error_signal.emit(f'uncertain status: {stat}')
