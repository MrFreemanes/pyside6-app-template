import sys
import multiprocessing as mp

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from core.workers.worker import worker
from utils.bridge import Bridge


def main():
    task_q = mp.Queue()
    result_q = mp.Queue()

    w = mp.Process(target=worker, args=(task_q, result_q), daemon=True)
    w.start()

    app = QApplication(sys.argv)

    window = MainWindow(Bridge(task_q, result_q))
    window.show()

    app.exec()

    w.terminate()
    w.join(timeout=1)


if __name__ == '__main__':
    main()
