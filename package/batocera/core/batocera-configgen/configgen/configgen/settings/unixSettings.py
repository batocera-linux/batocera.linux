from __future__ import annotations

import io
import logging
import re
import typing
from dataclasses import InitVar, dataclass, field
from pathlib import Path

from ..utils.configparser import CaseSensitiveConfigParser

if typing.TYPE_CHECKING:
    from _typeshed import StrPath

_logger = logging.getLogger(__name__)

def _protect_string(string: str) -> str:
    return re.sub(r'[^A-Za-z0-9-\.]+', '_', string)

@dataclass(slots=True)
class UnixSettings:
    filename_or_path: InitVar[StrPath]
    separator: str = field(default='', kw_only=True)
    settings_path: Path = field(init=False)
    config: CaseSensitiveConfigParser = field(init=False)

    def __post_init__(self, filename_or_path: StrPath) -> None:
        self.settings_path = Path(filename_or_path)

        # use ConfigParser as backend.
        _logger.debug("Creating parser for %s", self.settings_path)
        self.config = CaseSensitiveConfigParser(interpolation=None, strict=False) # strict=False to allow to read duplicates set by users

        try:
            # TODO: remove me when we migrate to Python 3.13 and can use allow_unnamed_section=True
            # pretend where have a [DEFAULT] section
            file = io.StringIO()
            file.write('[DEFAULT]\n')

            with self.settings_path.open(encoding='latin1') as f:
                file.write(f.read())

            file.seek(0)

            self.config.read_file(file)
        except IOError as e:
            _logger.error(str(e))

    def write(self) -> None:
        with self.settings_path.open('w') as fp:
            try:
                for key, value in self.config.items('DEFAULT'):
                    fp.write(f"{key}{self.separator}={self.separator}{value!s}\n")
            except:
                # PSX Mednafen writes beetle_psx_hw_cpu_freq_scale = "100%(native)"
                # Python 2.7 is EOL and ConfigParser 2.7 takes "%(" as a won't fix error
                # TODO: clean that up when porting to Python 3
                _logger.error("Wrong value detected (after % char maybe?), ignoring.")

    def save(self, name: str, value: object) -> None:
        # at least for cheevos_password
        if "password" in name.lower():
            _logger.debug("Writing %s = ******** to %s", name, self.settings_path)
        else:
            _logger.debug("Writing %s = %s to %s", name, value, self.settings_path)
        # TODO: do we need proper section support? PSP config is an ini file
        self.config.set('DEFAULT', name, str(value))

    def disable_all(self, name: str) -> None:
        _logger.debug("Disabling %s from %s", name, self.settings_path)
        for key, _ in self.config.items('DEFAULT'):
            if key[0:len(name)] == name:
                self.config.remove_option('DEFAULT', key)

    def remove(self, name: str) -> None:
        self.config.remove_option('DEFAULT', name)

    def load_all(self, name: str, includeName: bool = False) -> dict[str, str]:
        _logger.debug("Looking for %s.* in %s", name, self.settings_path)
        res: dict[str, str] = {}
        for key, value in self.config.items('DEFAULT'):
            m = re.match(rf"^{_protect_string(name)}\.(.+)", _protect_string(key))
            if m:
                if includeName:
                    res[f"{name}.{m.group(1)}"] = value;
                else:
                    res[m.group(1)] = value;

        return res
