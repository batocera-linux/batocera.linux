from __future__ import annotations

import logging
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def setup_logging() -> Iterator[None]:
    logger = logging.getLogger(__name__.split('.')[0])

    try:
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
        logger.setLevel(logging.DEBUG)
        logger.addHandler(stdout)
        logger.addHandler(stderr)

        yield
    finally:
        handlers = logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)
