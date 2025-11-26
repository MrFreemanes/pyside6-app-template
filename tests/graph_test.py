from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from gui.widgets.graphs.graph import Graph


class GraphTest(TestCase):
    def test_plot_realtime(self):
        plot_realtime = Graph.plot_realtime
        self_mock = MagicMock()
        self_mock.x = [0]
        self_mock.y = [1]
        new_x, new_y = 1, 2

        plot_realtime(self_mock, new_x, new_y)

        self.assertEqual(self_mock.x, [0, 1])
        self.assertEqual(self_mock.y, [1, 2])

        self_mock.ax.relim.assert_called_once()
        self_mock.ax.autoscale.assert_called_once()

        self_mock.line.set_data.assert_called_once_with(self_mock.x, self_mock.y)
        self_mock.canvas.draw_idle.assert_called_once()

    def test_plot_final(self):
        plot_final = Graph.plot_final
        self_mock = Mock()
        x, y = 10, 20
        plot_final(self_mock, x, y)

        self_mock.x.append.assert_called_once_with(x)
        self_mock.y.append.assert_called_once_with(y)

        self_mock.line.set_data.assert_called_once_with(self_mock.x, self_mock.y)
        self_mock.autoscale.assert_called_once()

        self_mock.x.clear.assert_called_once()
        self_mock.y.clear.assert_called_once()
