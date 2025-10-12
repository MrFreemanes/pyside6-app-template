from abc import ABC, abstractmethod

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout


class BaseGraph(ABC):
    def __init__(self, target_widget: QWidget, title: str = 'График'):
        self.target_widget = target_widget
        self.title = title

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(self.title)

        layout = target_widget.layout()

        if layout is None:
            layout = QVBoxLayout()
            self.target_widget.setLayout(layout)
        else:
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                w = item.widget()
                if isinstance(w, FigureCanvas):
                    layout.removeWidget(w)

        layout.addWidget(self.canvas)

    def clear(self) -> None:
        self.ax.clear()
        self.ax.set_title(self.title)
        self.canvas.draw_idle()

    def set_label(self, x_label: str, y_label: str) -> None:
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.canvas.draw_idle()

    def set_title(self, title: str) -> None:
        self.title = title
        self.ax.set_title(self.title)
        self.canvas.draw_idle()

    def show_grid(self, on: bool = True):
        self.ax.grid(on)
        self.canvas.draw_idle()

    def autoscale(self):
        self.ax.relim()
        self.ax.autoscale()
        self.canvas.draw_idle()

    @abstractmethod
    def plot_final(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def plot_realtime(self, *args, **kwargs) -> None:
        pass
