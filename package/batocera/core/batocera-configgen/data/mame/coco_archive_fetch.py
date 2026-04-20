#!/usr/bin/env python3
"""
Fetch xroar_config from colorcomputerarchive.com pages, download each zip,
compute SHA1 of the disk0 file inside, and produce a JSON indexed by SHA1.
"""

import argparse
import hashlib
import io
import json
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

URLS = [
    "https://colorcomputerarchive.com/repo/Disks/Games/",
    "https://colorcomputerarchive.com/repo/Disks/Games/French/",
    "https://colorcomputerarchive.com/repo/Disks/Games/French/Alice%20Software/",
    "https://colorcomputerarchive.com/repo/Disks/Games/Infocom%20Adventures/",
    "https://colorcomputerarchive.com/repo/Disks/Games/Infocom%20Adventures/64%20column%20(Coco%203)/",
    "https://colorcomputerarchive.com/repo/Disks/Games/Inufuto/",
    "https://colorcomputerarchive.com/repo/Disks/Games/Portuguese/",
    "https://colorcomputerarchive.com/repo/Disks/Games/Scott%20Adams%20Adventures/",
    "https://colorcomputerarchive.com/repo/Disks/Games/Sierra%20Games/"
    # "https://colorcomputerarchive.com/repo/Disks/Applications/",
]

OUTPUT    = Path("coco_sha1_map.json")
CACHE_DIR = Path("coco_zip_cache")

WORKERS = 8  # parallel downloads


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def download_zip(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())


def sha1_of_bytes(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def extract_xroar_config(html: str) -> list[dict]:
    match = re.search(r"xroar_config\s*=\s*(\{)", html)
    if not match:
        raise ValueError("xroar_config not found in page")
    data, _ = json.JSONDecoder().raw_decode(html, match.start(1))
    files = data.get("files", [])
    if not isinstance(files, list):
        raise ValueError(f"xroar_config.files is not a list: {type(files)}")
    return files


def decode_basic(value: str) -> str:
    return value.replace("%5Cr", "\n").replace("%5cr", "\n").replace("%22", '"')


def process_entry(base_url: str, entry: dict) -> list[tuple[str, dict]]:
    """Download zip, compute SHA1 for every DSK inside, return list of (sha1, entry)."""
    zip_filename = entry.get("filename")
    if not zip_filename or not entry.get("disk0"):
        return []

    zip_url  = base_url + urllib.parse.quote(zip_filename)
    zip_path = CACHE_DIR / zip_filename

    # Download (use cache if already present)
    if not zip_path.exists():
        try:
            download_zip(zip_url, zip_path)
        except Exception as exc:
            print(f"  DOWNLOAD ERROR {zip_filename}: {exc}", file=sys.stderr)
            return []

    # Build decoded entry once (basic field URL-decoding)
    base_entry = {**entry}
    if "basic" in base_entry:
        base_entry["basic"] = decode_basic(base_entry["basic"])

    # Hash every DSK file found in the zip
    results: list[tuple[str, dict]] = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            dsk_names = [n for n in zf.namelist()
                         if Path(n).suffix.lower() == ".dsk" and not n.endswith("/")]
            if not dsk_names:
                print(f"  NO DSK in zip {zip_filename}", file=sys.stderr)
                return []
            for name in dsk_names:
                try:
                    data = zf.read(name)
                    sha1 = sha1_of_bytes(data)
                    results.append((sha1, base_entry))
                except Exception as exc:
                    print(f"  READ ERROR {zip_filename}/{name}: {exc}", file=sys.stderr)
    except Exception as exc:
        print(f"  ZIP ERROR {zip_filename}: {exc}", file=sys.stderr)
        return []

    return results


def flatten_zip(zip_path: Path) -> bool:
    """Rewrite zip so all DSK files are at root (no subdirectory prefix).
    Returns True if the zip was modified, False if already flat or no DSKs found."""
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            dsk_names = [n for n in names
                         if Path(n).suffix.lower() == ".dsk" and not n.endswith("/")]
            if not dsk_names:
                return False
            # Check if any DSK is nested, has directory entries, or is not deflated
            nested = [n for n in dsk_names if "/" in n]
            has_dir_entries = any(n.endswith("/") for n in names)
            not_deflated = any(i.compress_type != zipfile.ZIP_DEFLATED
                               for i in zf.infolist() if not i.filename.endswith("/"))
            if not nested and not has_dir_entries and not not_deflated:
                return False  # already flat, clean, and compressed

            # Build new zip in memory: keep non-DSK entries as-is,
            # write DSK entries at root (basename only)
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out:
                for info in zf.infolist():
                    if info.filename.endswith("/"):
                        continue  # skip directory entries
                    data = zf.read(info.filename)
                    if Path(info.filename).suffix.lower() == ".dsk":
                        flat_name = Path(info.filename).name
                        out.writestr(flat_name, data)
                    else:
                        out.writestr(info, data)

        zip_path.write_bytes(buf.getvalue())
        return True
    except Exception as exc:
        print(f"  FLATTEN ERROR {zip_path.name}: {exc}", file=sys.stderr)
        return False


def flatten_dir(target_dir: Path) -> None:
    """Flatten all zips in target_dir that have DSK files in subdirectories."""
    zips = sorted(target_dir.glob("*.zip"))
    print(f"Scanning {len(zips)} zip files in {target_dir} …", file=sys.stderr)
    modified = 0
    for zip_path in zips:
        if flatten_zip(zip_path):
            modified += 1
            print(f"  Flattened: {zip_path.name}", file=sys.stderr)
    print(f"\nDone. {modified}/{len(zips)} zips flattened.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Fetch CoCo disk archive and build SHA1 map.")
    parser.add_argument("--flatten", metavar="DIR", nargs="?", const=str(CACHE_DIR),
                        help="Flatten DSK files to zip root in DIR (default: cache dir). "
                             "Does not fetch or hash — just rewrites zips.")
    args = parser.parse_args()

    if args.flatten is not None:
        flatten_dir(Path(args.flatten))
        return

    CACHE_DIR.mkdir(exist_ok=True)

    # Collect all entries from all URLs
    all_entries: list[tuple[str, dict]] = []  # (base_url, entry)
    for url in URLS:
        print(f"Fetching {url} …", file=sys.stderr)
        try:
            html = fetch_text(url)
            files = extract_xroar_config(html)
        except Exception as exc:
            print(f"  ERROR: {exc}", file=sys.stderr)
            continue
        print(f"  {len(files)} entries", file=sys.stderr)
        for entry in files:
            if entry.get("disk0"):
                all_entries.append((url, entry))
            else:
                print(f"  SKIP (no disk0): {entry.get('filename', '?')}", file=sys.stderr)

    print(f"\nDownloading & hashing {len(all_entries)} zips with {WORKERS} workers …", file=sys.stderr)

    result: dict[str, dict] = {}
    conflicts = 0
    done = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(process_entry, base_url, entry): entry
                   for base_url, entry in all_entries}
        for future in as_completed(futures):
            done += 1
            if done % 100 == 0 or done == len(all_entries):
                print(f"  {done}/{len(all_entries)}", file=sys.stderr)
            for sha1, entry in future.result():
                if sha1 in result:
                    conflicts += 1
                    print(
                        f"  SHA1 CONFLICT {sha1}: {result[sha1]['filename']!r} vs {entry['filename']!r}",
                        file=sys.stderr,
                    )
                else:
                    result[sha1] = entry

    print(f"\n{len(result)} SHA1 entries ({conflicts} conflict(s)) written to {OUTPUT}", file=sys.stderr)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
