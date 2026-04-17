from core.workers.base_worker import BaseWorker


class Writer(BaseWorker):
    @BaseWorker.register_task('save')
    def save(self) -> None:
        pass
