from __future__ import annotations

import logging
import subprocess
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pyudev

if TYPE_CHECKING:
    from types import TracebackType

    from ..generators.Generator import Generator

_logger = logging.getLogger(__name__)

@dataclass(slots=True)
class virtualmouse(AbstractContextManager[None, None]):
    __proc = None

    generator: Generator

    def __enter__(self) -> None:

        if hasattr(self.generator, 'has_virtualmouse') and not self.generator.has_virtualmouse():
           return

        _logger.info("Create virtual mouse")
        create_cmd = ["/usr/bin/evsieve"]
        context = pyudev.Context()

        for device in context.list_devices(subsystem='input').match_property('ID_INPUT_MOUSE', '1'):
            if device.sys_name.startswith('event'):
                create_cmd.extend(['--input', '/dev/input/' + device.sys_name])

        create_cmd.extend(['--output',
                           'rel:x',
                           'rel:y',
                           'btn:left',
                           'btn:middle',
                           'btn:right',
                           'name=Virtual_Multi_Mouse',
                           'create-link=/dev/input/Virtual_Multi_Mouse']
        )
        self.__proc = subprocess.Popen(create_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        if self.__proc:
            _logger.info(f"killing virtual mouse process {self.__proc.pid}")
            self.__proc.kill()
            self.__proc.communicate()
