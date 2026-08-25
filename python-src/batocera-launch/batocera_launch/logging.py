from __future__ import annotations

import errno
import io
import logging
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, TextIO

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


@contextmanager
def setup_logging() -> Generator[None]:
    """
    Configure logging with EPIPE-tolerant stdout/stderr and handlers.
    - DEBUG..INFO to stdout
    - WARNING..CRITICAL to stderr
    Also replaces sys.stdout/sys.stderr to protect non-logging writes.
    """
    # Replace sys.stdout/sys.stderr globally to protect any print() or library writes
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = EpipeTolerantTextIO(sys.stdout)
    sys.stderr = EpipeTolerantTextIO(sys.stderr)

    logger = logging.getLogger()
    original_handlers = list(logger.handlers)

    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(
        fmt='[{asctime}] [{levelname:<7}] ({name}:{funcName}:{lineno}): {message}',
        datefmt=date_format,
        style='{',
    )

    for h in original_handlers:
        logger.removeHandler(h)

    error_level = logging.WARNING

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
        from batocera_common.paths import LOGS

        file_handler = logging.FileHandler(filename=LOGS / 'batocera-launch.log', encoding='utf-8', mode='w')
        file_handler.setLevel(logging.NOTSET)  # Log all messages to the one file
        file_handler.setFormatter(formatter)
        file_handler.addFilter(lambda r: r.name != 'emulator')  # Exclude emulator logs from main log

        logger.addHandler(file_handler)

        emulator_file_handler = logging.FileHandler(
            filename=LOGS / 'batocera-launch-emulator.log', encoding='utf-8', mode='w'
        )
        emulator_file_handler.setLevel(logging.NOTSET)  # Log all messages to the one file
        emulator_file_handler.setFormatter(
            logging.Formatter(
                # Just log the message and timestamp for emulator logs, no need for function/line info
                fmt='[{asctime}] {message}',
                datefmt=date_format,
                style='{',
            )
        )
        emulator_file_handler.addFilter(lambda r: r.name == 'emulator')  # Only include emulator logs

        logger.addHandler(emulator_file_handler)
    except OSError:
        logger.exception('Could not set up log files')

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
