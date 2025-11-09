from PySide6.QtWidgets import QMenu, QWidget
from PySide6.QtCore import Qt


def attach_context_menu(widget: QWidget, action: dict) -> None:
    """
    Привязка нового контекстного меню к виджету

    Как использовать:
    attach_context_menu(
        self.widget,
        {
            "Сделать что-то": self.do_something,
            "Другое действие": lambda: print("Нажато")
        }
    )

    :param widget: Qt-виджет
    :param action: dict {"Название действия": callback}
    :return:
    """

    widget.setContextMenuPolicy(Qt.CustomContextMenu)

    def show_menu(pos):
        menu = QMenu(widget)
        for name, callback in action.items():
            menu.addAction(name, callback)
        menu.exec(widget.mapToGlobal(pos))

    widget.customContextMenuRequested.connect(show_menu)
