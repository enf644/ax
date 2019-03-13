"""Initiate loguru"""
import sys
from loguru import logger
from pathlib import Path
import backend.misc as ax_misc

# TODO Get settings from app.yaml. Get path to log files.


def init_logger(
    logs_filename: str,
    logs_absolute_path: str,
    logs_level: str
):
    """Initiate loguru"""
    config = {
        "handlers": [
            {
                'sink': sys.stdout,
                'colorize': 'True',
                'format': '⛏️  | {level} | <level>{message}</level>',
                'backtrace': 'False'
            }
        ],
        "extra": {"user": "someone"}
    }

    if logs_filename is not None:
        log_path = ax_misc.path('backend/logs/' + logs_filename)
        if logs_absolute_path is not None:
            log_path = str(Path(logs_absolute_path) / logs_filename)

        # TODO add rotation and retention, compression from app.yaml
        file_handler = {
            'sink': log_path,
            'serialize': 'True',
            'rotation': '100 MB',
            'enqueue': 'True',
            'backtrace': 'True',
            'level': logs_level
        }
        config['handlers'].append(file_handler)

    logger.configure(**config)
