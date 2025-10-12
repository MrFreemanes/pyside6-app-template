from PySide6.QtWidgets import QWidget

from gui.widgets.graph.base_graph import BaseGraph


class Graph(BaseGraph):
    """
    Пример реализации Класса BaseGraph.
    """

    def __init__(self, target_widget: QWidget, *, title: str = 'График'):
        super().__init__(target_widget, title)

        self.x = []
        self.y = []

    def plot_realtime(self, new_x: int, new_y: int) -> None:
        """Отрисовка графика при получении промежуточных данных"""
        self.clear()

        self.x.append(new_x)
        self.y.append(new_y)

        self.ax.plot(self.x, self.y, color='blue')
        self.autoscale()

    def plot_final(self, x: int, y: int) -> None:
        """Отрисовка графика с финальным видом"""
        self.clear()

        self.x.append(x)
        self.y.append(y)

        self.ax.plot(self.x, self.y, color='green')
        self.autoscale()

        self.x.clear()
        self.y.clear()
