from __future__ import annotations

from configparser import ConfigParser, RawConfigParser


class CaseSensitiveRawConfigParser(RawConfigParser):
    def optionxform(self, optionstr: str) -> str:
        return optionstr


class CaseSensitiveConfigParser(CaseSensitiveRawConfigParser, ConfigParser): ...
