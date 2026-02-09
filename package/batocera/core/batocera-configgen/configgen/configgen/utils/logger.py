from __future__ import annotations

import errno
import io
import logging
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, TextIO

if TYPE_CHECKING:
    from collections.abc import Iterator


class EpipeTolerantStreamHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            super().emit(record)
        except BrokenPipeError:
            return
        except OSError as e:
            if e.errno == errno.EPIPE:
                return
            raise

    def flush(self) -> None:
        try:
            super().flush()
        except BrokenPipeError:
            return
        except OSError as e:
            if e.errno == errno.EPIPE:
                return
            raise


class EpipeTolerantTextIO(io.TextIOBase):
    _raw: TextIO

    """
    Wrap a text stream to swallow BrokenPipeError/EPIPE on write/flush.
    """
    def __init__(self, raw: TextIO) -> None:
        self._raw = raw

    def write(self, s: str) -> int:
        try:
            return self._raw.write(s)
        except BrokenPipeError:
            return 0
        except OSError as e:
            if e.errno == errno.EPIPE:
                return 0
            raise

    def flush(self) -> None:
        try:
            return self._raw.flush()
        except BrokenPipeError:
            return None
        except OSError as e:
            if e.errno == errno.EPIPE:
                return None
            raise

    # Delegate other properties/methods
    @property
    def encoding(self) -> str:  # pyright: ignore[reportIncompatibleVariableOverride]
        return self._raw.encoding

    def fileno(self):
        return self._raw.fileno()

    def isatty(self):
        return self._raw.isatty()

    def close(self):
        try:
            self._raw.close()
        except BrokenPipeError:
            pass
        except OSError as e:
            if e.errno != errno.EPIPE:
                raise

    @property
    def closed(self) -> bool:
        return self._raw.closed


@contextmanager
def setup_logging() -> Iterator[None]:
    """
    Configure logging with EPIPE-tolerant stdout/stderr and handlers.
    - DEBUG..INFO to stdout
    - WARNING..CRITICAL to stderr
    Also replaces sys.stdout/sys.stderr to protect non-logging writes.
    """
    logger = logging.getLogger()
    original_handlers = list(logger.handlers)

    # Replace sys.stdout/sys.stderr globally to protect any print() or library writes
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = EpipeTolerantTextIO(sys.stdout)
    sys.stderr = EpipeTolerantTextIO(sys.stderr)

    error_level = logging.WARNING
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s (%(filename)s:%(lineno)d):%(funcName)s %(message)s"
    )

    for h in original_handlers:
        logger.removeHandler(h)

    stdout_handler = EpipeTolerantStreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(lambda r: r.levelno < error_level)

    stderr_handler = EpipeTolerantStreamHandler(stream=sys.stderr)
    stderr_handler.setLevel(error_level)
    stderr_handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    try:
        yield
    finally:
        # Clean up logging handlers
        for h in logger.handlers[:]:
            try:
                h.flush()
            except Exception:
                pass
            h.close()
            logger.removeHandler(h)

        # Optionally restore prior handlers
        for h in original_handlers:
            logger.addHandler(h)

        # Restore original stdout/stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr

