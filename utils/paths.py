import os

from config.config import NAME_APP


def path_to_dir() -> str:
    """Путь к папке AppData/Roaming/{name} и ее создание."""
    appdata_path = os.getenv("APPDATA")
    log_dir = os.path.join(appdata_path, NAME_APP)
    return log_dir


def path_to_log(name_file: str) -> str:
    """Путь к файлам .log в папке logs."""
    log_dir = os.path.join(path_to_dir(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    return os.path.join(log_dir, name_file)
