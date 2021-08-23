import logging
import sys


def get_logger(module_name: str) -> logging.Logger:
    # The logging level that separates stdout from stderr: stdout < error_level <= stderr
    error_level = logging.WARNING
    # Common formatter shared by handlers
    formatter = logging.Formatter("%(asctime)s %(levelname)s (%(filename)s:%(lineno)d):%(funcName)s %(message)s")
    # Configure stdout handler
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(formatter)
    stdout.setLevel(logging.DEBUG)
    stdout.addFilter(lambda record: record.levelno < error_level)  # Keep error logs out of stdout
    # Configure stderr handler
    stderr = logging.StreamHandler(sys.stderr)
    stderr.setFormatter(formatter)
    stderr.setLevel(error_level)
    # Configure logger
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout)
    logger.addHandler(stderr)
    return logger
