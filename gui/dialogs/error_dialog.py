from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton


class ErrorDialog(QDialog):
    """
    Всплывающее окно, блокирует родительский интерфейс.
    Используется для информирования об ошибках.
    """

    def __init__(self, message: str):
        super().__init__()
        self.setWindowTitle('Ошибка')
        self.setModal(True)  # Блокирует родительское окно
        self.resize(210, 100)

        _btn = QPushButton('Закрыть')
        _btn.clicked.connect(self.accept)

        _layout = QVBoxLayout()
        _layout.addWidget(QLabel(message))
        _layout.addWidget(_btn)

        self.setLayout(_layout)
