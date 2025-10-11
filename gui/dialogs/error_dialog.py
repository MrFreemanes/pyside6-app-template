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

        btn = QPushButton('Закрыть')
        btn.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))
        layout.addWidget(btn)

        self.setLayout(layout)
