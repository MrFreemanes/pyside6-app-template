from PySide6.QtWidgets import QWidget

from gui.widgets.graphs.base_graph import BaseGraph
from gui.helpers.widget_overrides import attach_context_menu


class Graph(BaseGraph):
    """
    Пример реализации Класса BaseGraph.
    Изменено контекстное меню виджета FigureCanvas (self._canvas).
    """

    def __init__(self, target_widget: QWidget, *, title: str = 'График'):
        super().__init__(target_widget, title)

        self.x = []
        self.y = []

        (self.line,) = self.ax.plot([], [], color='blue')

        self.show_grid()

        attach_context_menu(self.canvas, {'Сохранить график': self.save_graph})

    def plot_realtime(self, new_x: int, new_y: int) -> None:
        """Отрисовка графика при получении промежуточных данных"""
        self.x.append(new_x)
        self.y.append(new_y)

        if len(self.x) % 2 == 0:
            self.ax.relim()
            self.ax.autoscale()

        self.line.set_data(self.x, self.y)
        self.canvas.draw_idle()

    def plot_final(self, x: int, y: int) -> None:
        """Отрисовка финального графика"""
        self.x.append(x)
        self.y.append(y)

        self.line.set_data(self.x, self.y)
        self.autoscale()

        self.x.clear()
        self.y.clear()
