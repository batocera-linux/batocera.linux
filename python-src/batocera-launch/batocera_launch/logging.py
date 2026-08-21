from __future__ import annotations

import errno
import io
import logging
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, TextIO

from batocera_common.paths import LOGS

if TYPE_CHECKING:
    from collections.abc import Generator


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
    def encoding(self) -> str:  # type: ignore[override]  # pyright: ignore[reportIncompatibleVariableOverride]
        return self._raw.encoding

    def fileno(self) -> int:
        return self._raw.fileno()

    def isatty(self) -> bool:
        return self._raw.isatty()

    def close(self) -> None:
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


class EpipeTolerantStreamHandler(logging.StreamHandler[EpipeTolerantTextIO]):
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


class _LaunchFormatter(logging.Formatter):
    def __init__(self, fmt: str, emulator_fmt: str, datefmt: str) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt, style='{')
        self._emulator_formatter = logging.Formatter(fmt=emulator_fmt, datefmt=datefmt, style='{')

    def format(self, record: logging.LogRecord) -> str:
        if record.name == 'emulator':
            return self._emulator_formatter.format(record)

        return super().format(record)


@contextmanager
def setup_logging() -> Generator[None]:
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

    formatter = _LaunchFormatter(
        '[{asctime}] [{levelname:<7}] ({name}:{funcName}:{lineno}): {message}',
        '[{asctime}] [{levelname:<7}] ({name}): {message}',
        '%Y-%m-%d %H:%M:%S',
    )

    for h in original_handlers:
        logger.removeHandler(h)

    error_level = logging.WARNING

    stdout_handler = EpipeTolerantStreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(lambda r: r.levelno < error_level)

    file_logger = logging.FileHandler(filename=LOGS / 'batocera-launch.log', encoding='utf-8', mode='a')
    file_logger.setLevel(logging.DEBUG)
    file_logger.setFormatter(formatter)
    file_logger.addFilter(lambda r: r.levelno < error_level)

    stderr_handler = EpipeTolerantStreamHandler(stream=sys.stderr)
    stderr_handler.setLevel(error_level)
    stderr_handler.setFormatter(formatter)

    err_file_logger = logging.FileHandler(filename=LOGS / 'batocera-launch-errors.log', encoding='utf-8', mode='a')
    err_file_logger.setLevel(error_level)
    err_file_logger.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    logger.addHandler(file_logger)
    logger.addHandler(err_file_logger)

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
