from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pyfakefs import helpers
from pyfakefs.fake_filesystem import FakeFilesystem, OSType
from pyfakefs.fake_filesystem_unittest import Patcher

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import ModuleType


@pytest.fixture
def fs_modules_to_reload() -> list[ModuleType] | None:
    return


@pytest.fixture
def fs(fs_modules_to_reload: list[ModuleType] | None, monkeypatch: pytest.MonkeyPatch) -> Iterator[FakeFilesystem]:
    with monkeypatch.context() as mp:
        # delete these so our fake filesystem does not inherit the temporary directory
        # of the machine running the tests
        mp.delenv('TMP', raising=False)
        mp.delenv('TMPDIR', raising=False)
        mp.delenv('TEMP', raising=False)

        # batocera runs as root
        helpers.set_uid(0)

        with Patcher(
            additional_skip_names=[
                'syrupy.utils',
                'syrupy.extensions.amber.serializer',
                'syrupy.extensions.image',
                'syrupy.extensions.single_file',
            ],
            modules_to_reload=fs_modules_to_reload,
            allow_root_user=True,
        ) as patcher:
            patcher.fs.os = OSType.LINUX  # pyright: ignore
            yield patcher.fs  # pyright: ignore

        helpers.reset_ids()
