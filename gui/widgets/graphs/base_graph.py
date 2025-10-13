from abc import ABC, abstractmethod

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout


class BaseGraph(ABC):
    def __init__(self, target_widget: QWidget, title: str = 'График'):
        # Параметры.
        self.target_widget = target_widget
        self.title = title

        # Окно графика.
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)

        # График.
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(self.title)

        # Определение layout.
        layout = target_widget.layout()

        if layout is None:  # проверка на наличие layout на виджете.
            layout = QVBoxLayout()
            self.target_widget.setLayout(layout)
        else:
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                w = item.widget()
                if isinstance(w, FigureCanvas):  # Замена layout если виджет уже имеет FigureCanvas
                    layout.removeWidget(w)
                    w.deleteLater()

        # Добавляем виджет на найденный layout
        layout.addWidget(self.canvas)

    @abstractmethod
    def plot_final(self, *args, **kwargs) -> None:
        """Отрисовка итогового графика."""
        pass

    @abstractmethod
    def plot_realtime(self, *args, **kwargs) -> None:
        """Отрисовка графика с промежуточными данными для наглядности."""
        pass

    def clear(self) -> None:
        """Отчищает оси координат. Обновляет название графика."""
        self.ax.clear()
        self.ax.set_title(self.title)
        self.canvas.draw_idle()

    def set_label(self, x_label: str, y_label: str) -> None:
        """Устанавливает имена осей."""
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.canvas.draw_idle()

    def set_title(self, title: str) -> None:
        """Устанавливает новое название графика"""
        self.title = title
        self.ax.set_title(self.title)
        self.canvas.draw_idle()

    def show_grid(self, on: bool = True) -> None:
        """Включает/выключает сетку на графике."""
        self.ax.grid(on)
        self.canvas.draw_idle()

    def autoscale(self) -> None:
        """Автоматически редактирует график."""
        self.ax.relim()
        self.ax.autoscale()
        self.canvas.draw_idle()

    def save_graph(self) -> None:
        # Реализовать сохранение графика
        pass
