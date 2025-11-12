import sys
import multiprocessing as mp
import logging
from logging import config

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from core.workers.worker import Worker
from core.bridges.bridge import Bridge
from logs.logger_cfg import cfg

logging.config.dictConfig(cfg)
logger = logging.getLogger('log_main')


def main():
    task_q = mp.Queue(maxsize=3)
    result_q = mp.Queue()

    worker = Worker(task_q, result_q)
    w = mp.Process(target=worker.run, daemon=True)
    w.start()

    app = QApplication(sys.argv)
    window = MainWindow(Bridge(task_q, result_q, interval=50))
    window.show()
    app.exec()

    worker.stop()
    w.terminate()
    w.join(timeout=1)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        logger.exception('MAIN_ERROR: %s', err)
