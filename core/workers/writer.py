from core.workers.base_worker import BaseWorker


class Writer(BaseWorker):
    """
    Пример использования 2-го процесса помимо Worker.
    writer = Writer(task_q, result_q)
    worker = Worker(task_q, result_q)
    p1 = mp.Process(target=writer.run, daemon=True)
    p2 = mp.Process(target=worker.run, daemon=True)
    p1.start()
    p2.start()
    ...
    p1.stop()
    p2.stop()
    """

    @BaseWorker.register_task('save')
    def save(self) -> None:
        pass
