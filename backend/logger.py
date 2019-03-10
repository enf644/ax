"""Initiate loguru"""
import sys
from loguru import logger

# TODO Get settings from app.yaml. Get path to log files.


def init_logger():
    """Initiate loguru"""
    config = {
        "handlers": [
            {
                'sink': sys.stdout,
                'colorize': 'True',
                'format': '⛏️ | {level} | <level>{message}</level>',
                'backtrace': 'False'
            },
            # {
            #     'sink': 'ax_logs.log',
            #     'serialize': 'True',
            #     'rotation': '100 MB',
            #     'enqueue': 'True',
            #     'backtrace': 'True'
            # },
        ],
        "extra": {"user": "someone"}
    }

    logger.configure(**config)
