from PySide6.QtWidgets import QMenu, QWidget
from PySide6.QtCore import Qt


def attach_context_menu(widget: QWidget, action: dict) -> None:
    """
    Привязка нового контекстного меню к виджету.
    Контекстное меню вызывается правой кнопкой мыши при нажатии на виджет.

    Как использовать:
    attach_context_menu(
        self.widget,
        {
            "Первое действие": self.do_something,
            "Второе действие": lambda: print("Hi")
        }
    )

    :param widget: Qt-виджет
    :param action: dict {"Название действия": func}
    """

    widget.setContextMenuPolicy(Qt.CustomContextMenu)

    def show_menu(pos):
        menu = QMenu(widget)
        for name, callback in action.items():
            menu.addAction(name, callback)
        menu.exec(widget.mapToGlobal(pos))

    widget.customContextMenuRequested.connect(show_menu)
