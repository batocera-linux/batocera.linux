from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from ..batoceraPaths import BATOCERA_SHARE_DIR, CONFIGS, SAVES, mkdir_if_not_exists

if TYPE_CHECKING:
    from ..Emulator import Emulator


def precalibration_copyFile(src: Path, dst: Path) -> None:
    if src.exists() and not dst.exists():
        mkdir_if_not_exists(dst.parent)
        shutil.copyfile(src, dst)

def precalibration_copyDir(src: Path, dst: Path) -> None:
    if src.exists() and not dst.exists():
        mkdir_if_not_exists(dst.parent)
        shutil.copytree(src, dst)

def precalibration_copyFilesInDir(srcdir: Path, dstdir: Path, startWith: str, endWith: str) -> None:
    for src in srcdir.iterdir():
        if src.name.startswith(startWith): # and src.endswith(endswith):
            precalibration_copyFile(src, dstdir / src.name)

def precalibration(systemName: str, emulator: Emulator, core: str | None, rom: str | Path) -> None:
    dir = BATOCERA_SHARE_DIR / "guns-precalibrations" / systemName
    if not dir.exists():
        return

    rom = Path(rom)

    if systemName == "atomiswave":
        for suffix in ["nvmem", "nvmem2"]:
            src = dir / "reicast" / f"{rom.name}.{suffix}"
            dst = SAVES / "atomiswave" / "reicast" / f"{rom.name}.{suffix}"
            precalibration_copyFile(src, dst)

    elif systemName == "mame":
        target_dir: str | None = None
        if emulator == "mame":
            target_dir = "mame"
        elif emulator == "libretro":
            if core == "mame078plus":
                target_dir = "mame/mame2003-plus"
            elif core == "mame":
                target_dir = "mame/mame"

        if target_dir is not None:
            src = dir / "nvram" / rom.stem
            dst = SAVES / target_dir / "nvram" / rom.stem
            precalibration_copyDir(src, dst)
            srcdir = dir / "diff"
            dstdir = SAVES / target_dir / "diff"
            precalibration_copyFilesInDir(srcdir, dstdir, rom.stem + "_", ".dif")

    elif systemName == "model2":
        src = dir / "NVDATA" / f"{rom.name}.DAT"
        dst = SAVES / "model2" / "NVDATA" / f"{rom.name}.DAT"
        precalibration_copyFile(src, dst)

    elif systemName == "naomi":
        for suffix in ["nvmem", "eeprom"]:
            src = dir / "reicast" / f"{rom.name}.{suffix}"
            dst = SAVES / "naomi" / "reicast" / f"{rom.name}.{suffix}"
            precalibration_copyFile(src, dst)

    elif systemName == "supermodel":
        src = dir / "NVDATA" / f"{rom.stem}.nv"
        dst = SAVES / "supermodel" / "NVDATA" / f"{rom.stem}.nv"
        precalibration_copyFile(src, dst)

    elif systemName == "namco2x6":
        if emulator == "play":
            src = dir / "play" / rom.stem
            dst = CONFIGS / "play" / "Play Data Files" / "arcadesaves" / f"{rom.stem}.backupram"
            precalibration_copyFile(src, dst)
