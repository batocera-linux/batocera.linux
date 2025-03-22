from __future__ import annotations

from typing import ClassVar


class BaseBatoceraException(Exception):
    EXIT_CODE: ClassVar = 1

    @property
    def exit_code(self) -> int:
        return self.EXIT_CODE


class BatoceraException(BaseBatoceraException):
    @property
    def exit_code(self) -> int:
        if self.args and isinstance(self.args[0], str):
            return 250

        return self.EXIT_CODE

class UnexpectedEmulatorExit(BaseBatoceraException):
    EXIT_CODE = 200

class BadCommandLineArguments(BaseBatoceraException):
    EXIT_CODE = 201

class InvalidConfiguration(BaseBatoceraException):
    EXIT_CODE = 202

class UnknownEmulator(BaseBatoceraException):
    EXIT_CODE = 203

class MissingEmulator(BaseBatoceraException):
    EXIT_CODE = 204

class MissingCore(BaseBatoceraException):
    EXIT_CODE = 205
