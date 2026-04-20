from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import TypedDict

from ...batoceraPaths import mkdir_if_not_exists
from .mamePaths import (
    MAME_HASH_DIR,
    MESS_HASH_CACHE,
    MESS_SOFTLIST_MAP,
)

_logger = logging.getLogger(__name__)

_MAME_BUILTIN_HASH_DIR = Path("/usr/bin/mame/hash")
_CACHE_VERSION = 1


class RomInfo(TypedDict):
    softlist: str
    software: str
    media: str


# cdrom must precede cd so that _cdrom is not partially matched as _cd
_SOFTLIST_SUFFIX_RE = re.compile(
    r'_(cdrom|flop|cart|cass|disk|cd|rom|snap|hdd|quik|qd|cyl|ptp|ctape|card|ssd).*$'
)


def _machine_from_softlist(softlist: str) -> str:
    """Derive a machine name from a softlist name by stripping trailing media suffixes."""
    return _SOFTLIST_SUFFIX_RE.sub('', softlist)


def _lookup_rom(sha1: str) -> RomInfo | None:
    """Look up a SHA1 in the MAME software-list cache, building it if needed."""
    cache = _load_or_build_hash_cache()
    return cache.get(sha1)


def _build_config_args(config_args: list[dict], system, machine: str) -> list[str]:
    """
    Evaluate a config_args spec from messSoftlistMap.json against the live system
    config and return the resulting MAME command-line tokens.
    """
    result: list[str] = []
    for item in config_args:
        key     = item["key"]
        kind    = item.get("type", "str")
        skip_if = item.get("skip_if")

        only = item.get("only_machines")
        if only is not None and machine not in only:
            continue

        overrides: dict = item.get("machine_overrides", {}).get(machine, {})

        if kind == "bool":
            value = system.config.get_bool(key, item.get("default", False))
            if value:
                result += item.get("if_true", [])
            else:
                result += item.get("if_false", [])

        elif kind == "int":
            value = system.config.get_int(key) or 0
            if skip_if is not None and value == skip_if:
                continue
            if value:
                value = overrides.get("value_map", {}).get(str(value), value)
                if "max" in overrides:
                    value = min(value, overrides["max"])
                result += [s.replace("{value}", str(value)) for s in item.get("args", [])]

        else:  # str
            value = system.config.get_str(key) or item.get("default", "")
            if skip_if is not None and value == skip_if:
                continue
            if value:
                restriction = item.get("value_machine_restriction", {})
                if value in restriction and machine not in restriction[value]:
                    _logger.debug(
                        "MESS: skipping -%s %s: not supported on machine %s (allowed: %s)",
                        key, value, machine, restriction[value],
                    )
                    continue
                result += [s.replace("{value}", value) for s in item.get("args", [])]

    return result


def _build_rom_ext_args(rom_ext_args: list[dict], rom: Path) -> list[str]:
    """Emit static args based on the ROM file extension."""
    ext = rom.suffix.lower()
    result: list[str] = []
    for item in rom_ext_args:
        if ext in item.get("extensions", []):
            result += item.get("args", [])
    return result


def _load_softlist_map() -> dict:
    """Load the softlist→machine/media/autoboot mapping JSON."""
    if not MESS_SOFTLIST_MAP.exists():
        _logger.warning("MESS: messSoftlistMap.json not found at %s", MESS_SOFTLIST_MAP)
        return {}
    try:
        with MESS_SOFTLIST_MAP.open() as f:
            data = json.load(f)
        data.pop("_comment", None)
        return data
    except (json.JSONDecodeError, OSError) as exc:
        _logger.error("MESS: Failed to load messSoftlistMap.json: %s", exc)
        return {}


def _compute_sha1(rom: Path) -> str:
    """
    Compute the SHA1 of the ROM's raw data.

    For .zip archives, hashes the first file inside (as MAME stores sha1 of the
    uncompressed content, not the archive itself).
    """
    suffix = rom.suffix.casefold()

    if suffix == ".zip":
        try:
            with zipfile.ZipFile(rom, "r") as zf:
                names = [n for n in zf.namelist() if not n.endswith("/")]
                if names:
                    with zf.open(names[0]) as inner:
                        return _sha1_of_stream(inner)
        except (zipfile.BadZipFile, KeyError, OSError) as exc:
            _logger.warning("MESS: Could not read zip %s: %s – hashing archive directly", rom, exc)

    with rom.open("rb") as f:
        return _sha1_of_stream(f)


def _sha1_of_stream(stream) -> str:
    h = hashlib.sha1()
    for chunk in iter(lambda: stream.read(1 << 20), b""):
        h.update(chunk)
    return h.hexdigest()


def _get_hash_dirs() -> list[Path]:
    """Return candidate MAME hash directories, user-supplied first."""
    dirs = []
    if MAME_HASH_DIR.exists():
        dirs.append(MAME_HASH_DIR)
    if _MAME_BUILTIN_HASH_DIR.exists():
        dirs.append(_MAME_BUILTIN_HASH_DIR)
    return dirs


def _hash_dir_mtime() -> float:
    """Return the most recent mtime across all hash directories."""
    mtime = 0.0
    for d in _get_hash_dirs():
        try:
            mtime = max(mtime, d.stat().st_mtime)
        except OSError:
            pass
    return mtime


def _load_or_build_hash_cache() -> dict[str, RomInfo]:
    """Load the SHA1→RomInfo cache from disk, rebuilding if stale."""
    if MESS_HASH_CACHE.exists():
        try:
            with MESS_HASH_CACHE.open() as f:
                data = json.load(f)
            if (
                data.get("_version") == _CACHE_VERSION
                and data.get("_mtime", 0) >= _hash_dir_mtime()
            ):
                return data.get("entries", {})
        except (json.JSONDecodeError, OSError):
            pass

    _logger.info("MESS: Building software-list hash cache (this may take a moment)…")
    t0 = time.monotonic()
    entries = _build_hash_index()
    elapsed = time.monotonic() - t0
    _logger.info("MESS: Cache built with %d entries in %.1fs", len(entries), elapsed)

    payload = {
        "_version": _CACHE_VERSION,
        "_mtime":   _hash_dir_mtime(),
        "entries":  entries,
    }
    try:
        mkdir_if_not_exists(MESS_HASH_CACHE.parent)
        tmp = MESS_HASH_CACHE.with_suffix(".tmp")
        with tmp.open("w") as f:
            json.dump(payload, f)
        tmp.replace(MESS_HASH_CACHE)
    except OSError as exc:
        _logger.warning("MESS: Could not write hash cache: %s", exc)

    return entries


def _build_hash_index() -> dict[str, RomInfo]:
    """Parse all MAME software-list XMLs and build a sha1→RomInfo mapping."""
    index: dict[str, RomInfo] = {}

    for hash_dir in _get_hash_dirs():
        for xml_file in sorted(hash_dir.glob("*.xml")):
            softlist_name = xml_file.stem
            try:
                context = ET.iterparse(xml_file, events=("start",))
                current_software: str = ""
                current_media: str = ""
                for _, elem in context:
                    tag = elem.tag
                    if tag == "software":
                        current_software = elem.get("name", "")
                    elif tag == "part":
                        current_media = elem.get("name", "")
                    elif tag == "rom":
                        sha1 = (elem.get("sha1") or "").lower()
                        if sha1 and current_software and sha1 not in index:
                            index[sha1] = RomInfo(
                                softlist=softlist_name,
                                software=current_software,
                                media=current_media,
                            )
            except ET.ParseError as exc:
                _logger.warning("MESS: Skipping malformed XML %s: %s", xml_file, exc)

    return index
