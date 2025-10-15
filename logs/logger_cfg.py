import os


def path_to_file(name: str) -> str:
    APP_NAME = "MyApp"

    # Путь к папке в AppData
    appdata_path = os.getenv("APPDATA")
    log_dir = os.path.join(appdata_path, APP_NAME, "logs")
    os.makedirs(log_dir, exist_ok=True)

    return os.path.join(log_dir, name)


cfg = {
    'version': 1,
    'formatters': {
        'console_msg': {
            'format': '%(asctime)s | %(levelname)7s | %(filename)s:%(funcName)s:%(lineno)s | %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S'
        },
        'file_msg': {
            'format': '%(asctime)s | %(levelname)7s | %(filename)s:%(funcName)s:%(lineno)s | %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'console_msg'
        },
        'file_main': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': path_to_file("main.log"),
            'formatter': 'file_msg',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 5,  # хранить 5 старых файлов
            'encoding': 'utf-8'
        },
        'file_gui': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': path_to_file("gui.log"),
            'formatter': 'file_msg',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 3,
            'encoding': 'utf-8'
        },
        'file_bridge': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': path_to_file("bridges.log"),
            'formatter': 'file_msg',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 3,
            'encoding': 'utf-8'
        },
        'file_worker': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': path_to_file("worker.log"),
            'formatter': 'file_msg',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 3,
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'log_main': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_main'],
            'propagate': False
        },
        'log_gui': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_gui'],
            'propagate': False
        },
        'log_bridge': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_bridge'],
            'propagate': False
        },
        'log_worker': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_worker'],
            'propagate': False
        }
    }
}
