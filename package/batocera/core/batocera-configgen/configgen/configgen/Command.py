from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

class Command:
    def __init__(self, array: Sequence[str | Path], env: Mapping[str, str | Path] = dict()):
        self.array = list(array)
        self.env = dict(env)

    def __str__(self):
        strings: list[str] = []

        for varName, varValue in self.env.items():
            strings.append(f"{varName}={varValue}")

        for value in self.array:
            strings.append(str(value))

        return " ".join(strings)
