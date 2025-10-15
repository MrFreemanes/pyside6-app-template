from PySide6.QtWidgets import QWidget

from gui.widgets.graphs.base_graph import BaseGraph
from gui.helpers.widget_overrides import attach_context_menu


class Graph(BaseGraph):
    """
    Пример реализации Класса BaseGraph.
    Изменено контекстное меню виджета FigureCanvas (self.canvas).
    """

    def __init__(self, target_widget: QWidget, *, title: str = 'График'):
        super().__init__(target_widget, title)

        self.x = []
        self.y = []

        self.show_grid()

        attach_context_menu(self.canvas, {'Сохранить график': self.save_graph})

    def plot_realtime(self, new_x: int, new_y: int) -> None:
        """Отрисовка графика при получении промежуточных данных"""
        self.clear()

        self.x.append(new_x)
        self.y.append(new_y)

        self.show_grid()
        self.ax.plot(self.x, self.y, color='blue')
        self.autoscale()

    def plot_final(self, x: int, y: int) -> None:
        """Отрисовка финального графика"""
        self.clear()

        self.x.append(x)
        self.y.append(y)

        self.show_grid()
        self.ax.plot(self.x, self.y, color='green')
        self.autoscale()

        self.x.clear()
        self.y.clear()

    def save_graph(self):
        print('Сохранено!')
