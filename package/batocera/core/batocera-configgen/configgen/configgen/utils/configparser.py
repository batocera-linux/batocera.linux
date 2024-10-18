from __future__ import annotations

from configparser import ConfigParser, RawConfigParser
from typing import TYPE_CHECKING


class CaseSensitiveRawConfigParser(RawConfigParser):
    # In order to keep the signature of __init__() during type checking,
    # but also modify optionxform, we only want to override __init__()
    # during runtime
    if not TYPE_CHECKING:
        def __init__(self, *args: object, **kwargs: object) -> None:
            super().__init__(*args, **kwargs)  # type: ignore

            # prevent conversion to lower case keys
            self.optionxform = lambda optionstr: optionstr


class CaseSensitiveConfigParser(CaseSensitiveRawConfigParser, ConfigParser):
    ...
