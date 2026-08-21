import io
import tarfile
import zipfile
from urllib.response import addinfourl

__all__ = ['Resources', 'open_tarfile', 'open_url', 'open_zipfile']

def open_zipfile(
    archive: zipfile.ZipFile | str,
    filename: str,
    directory: str | None = None,
) -> io.BytesIO: ...
def open_tarfile(
    archive: tarfile.TarFile | str,
    filename: str,
    directory: str | None = None,
    ftype: str | None = None,
) -> io.BytesIO: ...
def open_url(filename: str, basepath: str | None = None) -> addinfourl: ...

class Resources:
    files: dict[str, tuple[str | None, str | None, str]]
    def __init__(
        self,
        path: str | None = None,
        subdir: str | None = None,
        excludepattern: str | None = None,
    ) -> None: ...
    def add(self, filename: str) -> None: ...
    def add_file(self, filename: str) -> None: ...
    def add_archive(self, filename: str, typehint: str = 'zip') -> None: ...
    def get(self, filename: str) -> io.BytesIO: ...
    def get_filelike(self, filename: str) -> io.BytesIO | io.BufferedReader: ...
    def get_path(self, filename: str) -> str: ...
    def scan(
        self,
        path: str,
        subdir: str | None = None,
        excludepattern: str | None = None,
    ) -> None: ...
