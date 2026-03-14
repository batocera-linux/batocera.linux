from __future__ import annotations

import logging
import subprocess
import zipfile
from pathlib import Path
from typing import Final

_logger = logging.getLogger(__name__)

# The comprehensive list of known floppy disk extensions for the Atom system
_ATOM_FLOPPY_EXTENSIONS: Final = {
    '.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88',
    '.1dd', '.cqm', '.cqi', '.dsk', '.40t'
}
_7Z_EXECUTABLE: Final = Path('/usr/bin/7z')

def is_atom_floppy(rom: Path, /) -> bool:
    extension = rom.suffix.casefold()
    if extension in _ATOM_FLOPPY_EXTENSIONS:
        return True

    if extension == '.zip':
        try:
            with zipfile.ZipFile(rom, 'r') as zip_ref:
                for filename_in_zip in zip_ref.namelist():
                    if Path(filename_in_zip).suffix.lower() in _ATOM_FLOPPY_EXTENSIONS:
                        return True
        except zipfile.BadZipFile:
            _logger.warning('Could not read zip file: %s', rom)

    elif extension == '.7z':
        try:
            proc = subprocess.run([_7Z_EXECUTABLE, 'l', '-ba', str(rom)], capture_output=True, text=True, check=False)
            if proc.returncode == 0:
                for line in proc.stdout.splitlines():
                    if Path(line.strip()).suffix.lower() in _ATOM_FLOPPY_EXTENSIONS:
                        return True
            else:
                _logger.warning('7z command failed for %s: %s', rom, proc.stderr)
        except FileNotFoundError:
            _logger.error('The executable was not found at %s. Cannot inspect .7z files.', _7Z_EXECUTABLE)

    return False
