# -*- coding: utf-8 -*-
# !/usr/bin/python3

import os
import sys
import copy
import logging
import logging.handlers
from logging.handlers import RotatingFileHandler

LOGDIR = os.environ.get("LOGDIR", "./logs")

COLORS = {
    "CRITICAL": "\033[0;31m",
    "ERROR": "\033[1;91m",
    "WARNING": "\033[1;93m",
    "INFO": "\033[0;37m",
    "DEBUG": "\033[0;34m",
}


class LogFormatter(logging.Formatter):
    """Log Formatter class"""

    def format(self, record):
        record = copy.copy(record)
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = COLORS[levelname] + levelname + "\033[0m"
        return logging.Formatter.format(self, record)


class Logger:
    """Logger Class"""

    logger = logging.getLogger("GoogleImageDownloader")
    logger.setLevel(logging.DEBUG)

    logger.propagate = False
    logger.handlers = []

    logging.getLogger().setLevel(logging.WARNING)

    log_dir = os.path.abspath(LOGDIR)
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        sys.stderr.write(
            f"GoogleImageDownloader : ERROR : Failed to create log directory: {e}.\n"
        )
        sys.exit(1)

    sys.stderr.write(f"GoogleImageDownloader : INFO : Writing logs to {log_dir}.\n")

    # File
    file_formatter = logging.Formatter(
        "%(asctime)s : %(name)s : %(levelname)s : %(message)s"
    )
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "google_image_downloader.log"), "a", 2e7, 20
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Stdout
    stdout_formatter = LogFormatter(
        "%(asctime)s : %(name)s : %(levelname)s : %(message)s"
    )
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(stdout_formatter)
    logger.addHandler(stdout_handler)

    @staticmethod
    def debug(*args, **kwargs):
        Logger.logger.debug(*args, **kwargs)

    @staticmethod
    def info(*args, **kwargs):
        Logger.logger.info(*args, **kwargs)

    @staticmethod
    def warning(*args, **kwargs):
        Logger.logger.warning(*args, **kwargs)

    @staticmethod
    def error(*args, **kwargs):
        Logger.logger.error(*args, **kwargs)

    @staticmethod
    def critical(*args, **kwargs):
        Logger.logger.critical(*args, **kwargs)
