from unittest import TestCase, main
from unittest.mock import Mock, patch, MagicMock

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from gui.widgets.graphs.base_graph import BaseGraph


class TestGraph(BaseGraph):
    def plot_final(self, *args, **kwargs) -> None:
        pass

    def plot_realtime(self, *args, **kwargs) -> None:
        pass


class BaseGraphTest(TestCase):
    @patch('gui.widgets.graphs.base_graph.QVBoxLayout')
    @patch('gui.widgets.graphs.base_graph.Figure')
    @patch('gui.widgets.graphs.base_graph.FigureCanvas')
    def test_init(self, FigureCanvas_mock, Figure_mock, QVBoxLayout_mock):
        widget = MagicMock()
        widget.layout.return_value = None

        # figure
        figure_mock = Mock()
        ax_mock = Mock()
        figure_mock.add_subplot.return_value = ax_mock
        Figure_mock.return_value = figure_mock

        # canvas
        canvas_mock = Mock()
        FigureCanvas_mock.return_value = canvas_mock

        # layout
        layout_mock = Mock()
        QVBoxLayout_mock.return_value = layout_mock

        graph = TestGraph(widget)

        # test figure
        Figure_mock.assert_called_once_with(figsize=(5, 3))
        figure_mock.add_subplot.assert_called_once()
        ax_mock.set_title.assert_called_once()

        # test canvas
        FigureCanvas_mock.assert_called_once_with(figure_mock)

        # test layout
        widget.setLayout.assert_called_once_with(layout_mock)
        QVBoxLayout_mock.assert_called_once()
        layout_mock.addWidget.assert_called_once_with(canvas_mock)

    @patch('gui.widgets.graphs.base_graph.Figure')
    @patch('gui.widgets.graphs.base_graph.FigureCanvas')
    def test_init_replace_old_canvas(self, FigureCanvas_mock, Figure_mock):
        # TODO: тест с уже существующим FigureCanvas
        pass

    def test_clear(self):
        clear = TestGraph.clear
        self_mock = Mock()
        clear(self_mock)

        self_mock.ax.clear.assert_called_once()
        self_mock.ax.set_title.assert_called_once()
        self_mock._canvas.draw_idle.assert_called_once()

    def test_set_label(self):
        set_label = TestGraph.set_label
        self_mock = Mock()
        x_label, y_label = 'x', 'y'
        set_label(self_mock, x_label, y_label)

        self_mock.ax.set_xlabel.assert_called_once_with(x_label)
        self_mock.ax.set_ylabel.assert_called_once_with(y_label)
        self_mock._canvas.draw_idle.assert_called_once()

    def test_set_title(self):
        set_title = TestGraph.set_title
        self_mock = Mock()
        title = 'title'
        set_title(self_mock, title)

        self.assertEqual(self_mock._title, title)
        self_mock.ax.set_title.assert_called_once_with(title)
        self_mock._canvas.draw_idle.assert_called_once()

    def test_show_grid(self):
        show_grid = TestGraph.show_grid
        self_mock = Mock()
        show_grid(self_mock)

        self_mock.ax.grid.assert_called_once_with(True)
        self_mock._canvas.draw_idle.assert_called_once()

    def test_autoscale(self):
        autoscale = TestGraph.autoscale
        self_mock = Mock()
        autoscale(self_mock)

        self_mock.ax.relim.assert_called_once()
        self_mock.ax.autoscale.assert_called_once()
        self_mock._canvas.draw_idle.assert_called_once()

    @patch('gui.widgets.graphs.base_graph.QFileDialog')
    def test_save_graph(self, QFileDialog_mock):
        save_graph = TestGraph.save_graph
        self_mock = Mock()
        QFileDialog_mock.getSaveFileName.return_value = ('path', 'other')
        save_graph(self_mock)

        self.assertEqual(
            QFileDialog_mock.getSaveFileName.call_args[0][0],
            self_mock._target_widget
        )
        self_mock._figure.savefig.assert_called_once_with('path')

    @patch('gui.widgets.graphs.base_graph.QFileDialog')
    def test_save_graph_no_path(self, QFileDialog_mock):
        save_graph = TestGraph.save_graph
        self_mock = Mock()
        QFileDialog_mock.getSaveFileName.return_value = ('', '')
        save_graph(self_mock)

        self.assertEqual(
            QFileDialog_mock.getSaveFileName.call_args[0][0],
            self_mock._target_widget
        )
        self_mock._figure.savefig.assert_not_called()


if __name__ == '__main__':
    main()
