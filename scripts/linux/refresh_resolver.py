#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Iterable, Iterator, Mapping


# Clean ANSI coloring helper
def bold(text: object, /) -> str:
    return f'\033[1m{text!s}\033[0m'


def yellow(text: object, /) -> str:
    return f'\033[93m{text!s}\033[0m'


def red(text: object, /) -> str:
    return f'\033[91m{text!s}\033[0m'


def find_all_mk_files(project_dir: Path, /) -> dict[str, Path]:
    search_dirs = [
        'package/batocera',
        'buildroot/arch',
        'buildroot/boot',
        'buildroot/linux',
        'buildroot/package',
        'buildroot/toolchain',
    ]
    mk_files: dict[str, Path] = {}

    for search_dir in search_dirs:
        full_dir = project_dir / search_dir
        if full_dir.is_dir():
            for path in full_dir.rglob('*.mk'):
                # Exclude internal buildroot infrastructure files
                if path.name.startswith('pkg-') or path.name in ('Makefile.in', 'Makefile', 'sdk.mk'):
                    continue

                pkg_name = path.stem
                mk_files[pkg_name] = path

    return mk_files


def clean_tokens(tokens: Iterable[str], /) -> list[str]:
    """Filters out GNU Make variables, conditions, and invalid package names."""
    valid_pattern = re.compile(r'^[a-zA-Z0-9\-_]+$')
    return [t.strip() for t in tokens if valid_pattern.match(t.strip())]


def parse_mk_dependencies(
    all_mk_files: Mapping[str, Path], /
) -> tuple[dict[str, list[str]], dict[str, list[str]], list[str]]:
    dependencies: dict[str, list[str]] = {}
    provides_map: dict[str, list[str]] = {}
    kernel_modules: list[str] = []

    # Matches standard out-of-tree kernel modules
    kernel_module_regex = re.compile(r'\bkernel-module\b')

    for pkg_name, path in all_mk_files.items():
        try:
            content = path.read_text(errors='ignore')
        except Exception:
            continue

        # Register if it uses the kernel-module infra, or explicitly references kernel variables
        if kernel_module_regex.search(content) or 'LINUX_DIR' in content or 'LINUX_VERSION' in content:
            kernel_modules.append(pkg_name)

        # Normalize line continuations (\ followed by newline)
        content = re.sub(r'\\\s*\n', ' ', content)
        lines = content.split('\n')

        pkg_upper = pkg_name.upper().replace('-', '_')
        target_dep_var = f'{pkg_upper}_DEPENDENCIES'
        host_dep_var = f'HOST_{pkg_upper}_DEPENDENCIES'
        target_provides_var = f'{pkg_upper}_PROVIDES'
        host_provides_var = f'HOST_{pkg_upper}_PROVIDES'

        target_dep_regex = re.compile(rf'^\s*{target_dep_var}\s*(?:\+?=|=)\s*(.*)$')
        host_dep_regex = re.compile(rf'^\s*{host_dep_var}\s*(?:\+?=|=)\s*(.*)$')
        target_prov_regex = re.compile(rf'^\s*{target_provides_var}\s*(?:\+?=|=)\s*(.*)$')
        host_prov_regex = re.compile(rf'^\s*{host_provides_var}\s*(?:\+?=|=)\s*(.*)$')

        target_deps: list[str] = []
        host_deps: list[str] = []
        target_provides: list[str] = []
        host_provides: list[str] = []

        for line in lines:
            line_clean = line.split('#')[0].strip()

            m_target_dep = target_dep_regex.match(line_clean)
            if m_target_dep:
                target_deps.extend(m_target_dep.group(1).split())

            m_host_dep = host_dep_regex.match(line_clean)
            if m_host_dep:
                host_deps.extend(m_host_dep.group(1).split())

            m_target_prov = target_prov_regex.match(line_clean)
            if m_target_prov:
                target_provides.extend(m_target_prov.group(1).split())

            m_host_prov = host_prov_regex.match(line_clean)
            if m_host_prov:
                host_provides.extend(m_host_prov.group(1).split())

        target_deps = clean_tokens(target_deps)
        host_deps = clean_tokens(host_deps)
        target_provides = clean_tokens(target_provides)
        host_provides = clean_tokens(host_provides)

        if target_deps:
            dependencies[pkg_name] = list(set(target_deps))
        if host_deps:
            dependencies[f'host-{pkg_name}'] = list(set(host_deps))

        if target_provides:
            provides_map[pkg_name] = list(set(target_provides))
        if host_provides:
            provides_map[f'host-{pkg_name}'] = list(set(host_provides))

    return dependencies, provides_map, kernel_modules


def find_package_for_file(changed_file_path: Path, all_mk_files: Mapping[str, Path], /) -> str | None:
    """Maps a changed file path back to its parent package using a strict subdirectory descendant check."""
    changed_path = changed_file_path.resolve()

    best_pkg: str | None = None
    best_prefix_len = -1

    for pkg_name, mk_path in all_mk_files.items():
        pkg_dir = mk_path.parent.resolve()
        try:
            # Verify if the modified file path sits within this package directory
            changed_path.relative_to(pkg_dir)
            prefix_len = len(pkg_dir.parts)
            # Prefer the most specific/deepest folder match
            if prefix_len > best_prefix_len:
                best_prefix_len = prefix_len
                best_pkg = pkg_name
        except ValueError:
            continue

    return best_pkg


def get_changed_files(git_root: Path, days: int, /) -> Iterator[Path]:
    """Retrieves both committed files and any uncommitted staged/unstaged/untracked files."""
    changed_files: set[str] = set()

    # Committed files from the last N days
    try:
        out = subprocess.check_output(
            ['git', '-C', str(git_root), 'log', f'--since={days} days ago', '--name-only', '--format=%n'],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
        changed_files.update(line.strip() for line in out.splitlines() if line.strip())
    except Exception:
        pass

    # Uncommitted modifications (both staged and unstaged)
    try:
        out = subprocess.check_output(
            ['git', '-C', str(git_root), 'diff', 'HEAD', '--name-only'],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
        changed_files.update(line.strip() for line in out.splitlines() if line.strip())
    except Exception:
        pass

    # Untracked files
    try:
        out = subprocess.check_output(
            ['git', '-C', str(git_root), 'ls-files', '--others', '--exclude-standard'],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
        changed_files.update(line.strip() for line in out.splitlines() if line.strip())
    except Exception:
        pass

    for file_rel in sorted(changed_files):
        yield git_root / file_rel


def map_config_option_to_package(option: str, config_to_pkg: Mapping[str, str], /) -> str | None:
    """Maps a Buildroot Kconfig option (e.g. BR2_LINUX_KERNEL_... or BR2_PACKAGE_SDL2) to its package name."""
    # Core Buildroot subsystems
    if 'LINUX_KERNEL' in option or option == 'BR2_LINUX_KERNEL':
        return 'linux'
    if 'UBOOT' in option or option == 'BR2_TARGET_UBOOT':
        return 'uboot'

    # Package options (including host packages)
    if option.startswith('BR2_PACKAGE_'):
        content = option[len('BR2_PACKAGE_'):]
        is_host = False
        if content.startswith('HOST_'):
            content = content[len('HOST_'):]
            is_host = True

        # Sort keys descending by length to match the most specific package first
        for pkg_upper in sorted(config_to_pkg.keys(), key=len, reverse=True):
            if content == pkg_upper or content.startswith(pkg_upper + '_'):
                return f"host-{config_to_pkg[pkg_upper]}" if is_host else config_to_pkg[pkg_upper]

    return None


def get_changed_configs_in_file(git_root: Path, file_path: Path, days: int, /) -> set[str]:
    """Extracts changed Buildroot config options from committed logs and uncommitted diffs."""
    changed_options: set[str] = set()
    try:
        rel_path = file_path.resolve().relative_to(git_root.resolve())
        config_key_pattern = re.compile(r'^[+-](?![+-])\s*(?:#\s*)?(BR2_[A-Z0-9_]+)')

        # Fetch from committed logs
        out_log = subprocess.check_output(
            ['git', '-C', str(git_root), 'log', '-p', f'--since={days} days ago', '--', str(rel_path)],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
        for line in out_log.splitlines():
            if match := config_key_pattern.match(line):
                changed_options.add(match.group(1))

        # Fetch from uncommitted (staged + unstaged) edits
        out_diff = subprocess.check_output(
            ['git', '-C', str(git_root), 'diff', 'HEAD', '--', str(rel_path)],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
        for line in out_diff.splitlines():
            if match := config_key_pattern.match(line):
                changed_options.add(match.group(1))
    except Exception:
        pass
    return changed_options


def find_package_for_board_or_config(
    changed_file: Path,
    git_root: Path,
    all_mk_files: Mapping[str, Path],
    config_to_pkg: Mapping[str, str],
    days: int,
    /,
) -> set[str]:
    """Maps config-level and board-level file modifications back to their respective Buildroot packages."""
    resolved_packages: set[str] = set()
    changed_path = changed_file.resolve()

    # Check if the file is inside the 'configs' directory (e.g. batocera-*.board)
    configs_dir = (git_root / 'configs').resolve()
    try:
        changed_path.relative_to(configs_dir)
        is_config_file = True
    except ValueError:
        is_config_file = False

    if is_config_file:
        changed_configs = get_changed_configs_in_file(git_root, changed_file, days)
        for opt in changed_configs:
            if mapped_pkg := map_config_option_to_package(opt, config_to_pkg):
                resolved_packages.add(mapped_pkg)
        return resolved_packages

    # Check if the file is inside the 'board' directory (e.g. custom configs or patches)
    board_dir = (git_root / 'board').resolve()
    try:
        changed_path.relative_to(board_dir)
        is_board_file = True
    except ValueError:
        is_board_file = False

    if is_board_file:
        path_str = changed_path.as_posix()

        # Map package-specific patches under board/ (e.g. board/batocera/amlogic/patches/linux/0001-patch.patch)
        patches_match = re.search(r'/patches/([^/]+)/', path_str)
        if patches_match:
            pkg_name = patches_match.group(1)
            if pkg_name in all_mk_files:
                resolved_packages.add(pkg_name)
            return resolved_packages

        file_name_lower = changed_file.name.lower()

        # Map Linux kernel config files (e.g. linux.config, linux-meson64.config)
        if 'linux' in file_name_lower and ('config' in file_name_lower or file_name_lower.endswith('.config')):
            resolved_packages.add('linux')
            return resolved_packages

        # Map bootloader config files (e.g. u-boot.config, uboot-board.config)
        if ('u-boot' in file_name_lower or 'uboot' in file_name_lower) and ('config' in file_name_lower or file_name_lower.endswith('.config')):
            resolved_packages.add('uboot')
            return resolved_packages

    return resolved_packages


def get_git_modified_packages(project_dir: Path, days: int, all_mk_files: Mapping[str, Path], /) -> set[str]:
    modified_pkgs: set[str] = set()

    # Pre-build uppercase to lowercase package map for config-to-package translation
    config_to_pkg: dict[str, str] = {}
    for pkg_name in all_mk_files:
        pkg_upper = pkg_name.upper().replace('-', '_')
        config_to_pkg[pkg_upper] = pkg_name

    def process_repo(git_root: Path) -> None:
        for changed_file in get_changed_files(git_root, days):
            # Try matching standard packages first
            if pkg := find_package_for_file(changed_file, all_mk_files):
                modified_pkgs.add(pkg)
                continue

            # Check configuration or board directory mappings
            extra_pkgs = find_package_for_board_or_config(changed_file, git_root, all_mk_files, config_to_pkg, days)
            modified_pkgs.update(extra_pkgs)

    # Check main repository
    process_repo(project_dir)

    # Check Buildroot submodule
    buildroot_dir = project_dir / 'buildroot'
    if buildroot_dir.is_dir():
        process_repo(buildroot_dir)

    return modified_pkgs


def filter_built_packages(packages: Iterable[str], output_dir: Path, /) -> set[str]:
    build_dir = output_dir / 'build'
    per_package_dir = output_dir / 'per-package'

    built_pkgs: set[str] = set()

    build_subdirs = []
    if build_dir.is_dir():
        build_subdirs = [d.name for d in build_dir.iterdir() if d.is_dir()]

    per_package_subdirs: set[str] = set()
    if per_package_dir.is_dir():
        per_package_subdirs = {d.name for d in per_package_dir.iterdir() if d.is_dir()}

    for pkg in packages:
        pkg_norm = pkg.replace('_', '-').lower()
        
        # Check per-package directories
        matched_per_package = False
        for d in per_package_subdirs:
            if d.replace('_', '-').lower() == pkg_norm:
                built_pkgs.add(pkg)
                matched_per_package = True
                break
        if matched_per_package:
            continue

        # Check build subdirectories (lenient matching on hyphens vs underscores)
        for d in build_subdirs:
            d_norm = d.replace('_', '-').lower()
            if d_norm == pkg_norm or d_norm.startswith(pkg_norm + '-'):
                built_pkgs.add(pkg)
                break

    return built_pkgs


def collect_paths_to_delete(packages: Collection[str], output_dir: Path, /) -> list[Path]:
    build_dir = output_dir / 'build'
    per_package_dir = output_dir / 'per-package'

    paths_to_delete: list[Path] = []

    if per_package_dir.is_dir():
        try:
            p_subdirs = [d for d in per_package_dir.iterdir() if d.is_dir()]
        except Exception:
            p_subdirs = []

        for pkg in packages:
            pkg_norm = pkg.replace('_', '-').lower()
            for d in p_subdirs:
                if d.name.replace('_', '-').lower() == pkg_norm:
                    paths_to_delete.append(d)

    if build_dir.is_dir():
        try:
            b_subdirs = [d for d in build_dir.iterdir() if d.is_dir()]
        except Exception:
            b_subdirs = []

        for pkg in packages:
            pkg_norm = pkg.replace('_', '-').lower()
            for d in b_subdirs:
                d_norm = d.name.replace('_', '-').lower()
                if d_norm == pkg_norm or d_norm.startswith(pkg_norm + '-'):
                    paths_to_delete.append(d)

    return sorted(set(paths_to_delete))


def remove_directory(path: Path, /) -> None:
    def handle_remove_readonly(func: Callable[..., Any], p: str, exc_info: BaseException, /) -> None:
        try:
            Path(p).chmod(stat.S_IWRITE)
            func(p)
        except Exception:
            pass

    try:
        shutil.rmtree(path, onexc=handle_remove_readonly)
    except Exception as e:
        print(f'Error removing {path}: {e}', file=sys.stderr)


def get_reason_chain(pkg: str, reasons: Mapping[str, str], /) -> str:
    chain: list[str] = []
    curr = pkg
    while curr in reasons:
        parent = reasons[curr]

        if parent in ('git-modified', 'mandatory', 'provider-expansion', 'kernel-module', 'co-located-host'):
            chain.append(f'{curr} ({parent})')
            break

        chain.append(curr)
        curr = parent

    return ' -> '.join(chain)


def main() -> None:
    # Force immediate unbuffered line outputs to prevent logs hanging in pipe/Makefile subprocesses
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument('--project-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--days', type=int, default=1)
    parser.add_argument('--mandatory', default='')
    args = parser.parse_args()

    project_dir: Path = args.project_dir.resolve()
    output_dir: Path = args.output_dir.resolve()

    print('>>> Scanning workspace for package definitions...')
    all_mk_files = find_all_mk_files(project_dir)
    print(f'    Found {len(all_mk_files)} package definitions.')

    print('\n>>> Parsing dependencies and building reverse dependency graph...')
    dependencies, provides_map, kernel_modules = parse_mk_dependencies(all_mk_files)
    print(f'    Parsed {len(dependencies)} package dependencies.')
    print(f'    Detected {len(kernel_modules)} kernel-related modules:')
    print(f'      {", ".join(sorted(kernel_modules))}')

    print(f'\n>>> Detecting packages modified in git over the last {args.days} days...')
    modified = get_git_modified_packages(project_dir, args.days, all_mk_files)
    if modified:
        for m in sorted(modified):
            print(f'      - {m}')
    else:
        print('      (None detected)')

    mandatory: set[str] = set(args.mandatory.split())
    if mandatory:
        print('\n>>> Mandatory rebuild packages:')
        for m in sorted(mandatory):
            print(f'      - {m}')

    seed_packages = modified.union(mandatory)
    if not seed_packages:
        print('\nNo seed packages found to reset. Aborting.')
        sys.exit(0)

    # Dictionary to store the structural reason/parent chain for each reset package
    reasons: dict[str, str] = {}
    for pkg in modified:
        reasons[pkg] = 'git-modified'
    for pkg in mandatory:
        if pkg not in reasons:
            reasons[pkg] = 'mandatory'

    # If 'linux', 'linux-headers', or 'host-linux-headers' is in the seed packages, promote all
    # detected kernel modules to core seed packages. This guarantees they are evaluated and rebuilt
    if any(k in seed_packages for k in ('linux', 'linux-headers', 'host-linux-headers')):
        print('\n>>> Kernel-related changes detected. Elevating modules to core seed packages:')
        for km in sorted(kernel_modules):
            print(f'      - {km}')
            if km not in reasons:
                reasons[km] = 'kernel-module'
        seed_packages.update(kernel_modules)

    # Provider/Virtual package expansion
    provider_expansion: set[str] = set()
    for pkg in seed_packages:
        if pkg in provides_map:
            provider_expansion.update(provides_map[pkg])

    if provider_expansion:
        print('\n>>> Expanding virtual package providers:')
        for p in sorted(provider_expansion):
            print(f'      - {p}')
            if p not in reasons:
                reasons[p] = 'provider-expansion'
        seed_packages.update(provider_expansion)

    # Host Co-location check for seed packages
    # If a seed target package has a matching host variant built on disk, include it.
    host_seeds: set[str] = set()
    host_candidates = [f'host-{pkg}' for pkg in seed_packages if not pkg.startswith('host-')]
    built_host_packages = filter_built_packages(host_candidates, output_dir)
    for host_pkg in built_host_packages:
        host_seeds.add(host_pkg)
        if host_pkg not in reasons:
            reasons[host_pkg] = 'co-located-host'
    if host_seeds:
        print('\n>>> Co-locating host equivalents for modified packages:')
        for h in sorted(host_seeds):
            print(f'      - {h}')
        seed_packages.update(host_seeds)

    # Build Reverse Dependency Graph
    reverse_deps: dict[str, list[str]] = {}
    for pkg, deps in dependencies.items():
        for dep in deps:
            reverse_deps.setdefault(dep, []).append(pkg)

    # Recursive graph traversal (BFS) to find affected dependents
    to_reset = set(seed_packages)
    queue = list(seed_packages)

    def add_to_reset(pkg: str, parent: str):
        if pkg not in to_reset:
            to_reset.add(pkg)
            queue.append(pkg)
            reasons[pkg] = parent

            # Fallback hook: If 'linux', 'linux-headers', or 'host-linux-headers' is pulled in at any point:
            if pkg in ('linux', 'linux-headers', 'host-linux-headers'):
                for km in kernel_modules:
                    add_to_reset(km, 'kernel-module')

    while queue:
        current = queue.pop(0)
        for rdep in reverse_deps.get(current, []):
            add_to_reset(rdep, current)

    # Filter built packages
    final_packages = filter_built_packages(to_reset, output_dir)
    if not final_packages:
        print('\nNo active build outputs found on disk matching the affected packages. Nothing to reset.')
        sys.exit(0)

    # Active kernel module tracking diagnostic output
    active_modules = [pkg for pkg in final_packages if pkg in kernel_modules]
    if active_modules:
        print(f'\n>>> Found {len(active_modules)} active (previously built) kernel modules to reset:')
        for am in sorted(active_modules):
            print(f'      - {am}')

    # CASCADE PROTECTION: Check if deletion plan size is large
    if len(final_packages) > 30:
        print('\n' + yellow('========================================================'))
        print(yellow('⚠️  WARNING: LARGE DEPENDENCY CASCADE DETECTED'))
        print(yellow('========================================================'))
        print(f'A total of {bold(len(final_packages))} active packages will be reset and rebuilt.')
        print('This is usually triggered by modifications to low-level/core system libraries (such as mesa3d or udev).')
        print('--------------------------------------------------------')
        
        try:
            # Force prompt flush before requesting raw input
            print(
                'Would you like to perform a '
                + bold('Shallow Refresh')
                + ' instead?\n(Only resets modified seeds, skipping recursive dependents) [y/N]: ',
                end='',
                flush=True
            )
            response = input().strip().lower()
            if response in ('y', 'yes'):
                print('\n>>> Downgrading to Shallow Refresh...', flush=True)
                to_reset = seed_packages
                final_packages = filter_built_packages(to_reset, output_dir)
        except (KeyboardInterrupt, EOFError):
            print('\n\nRefresh aborted.')
            sys.exit(1)

    paths_to_delete = collect_paths_to_delete(final_packages, output_dir)

    print('\n========================================================')
    print('Surgical Refresh Deletion Plan')
    print('========================================================')
    print('The following directories will be permanently deleted:')

    # Track output directory names for cleaner reason mapping
    for path in paths_to_delete:
        try:
            rel_path = path.relative_to(project_dir)
        except ValueError:
            rel_path = path

        pkg_key = path.name
        # Match built package format (e.g. 'sdl3-3.4.2' -> 'sdl3')
        for pkg in final_packages:
            pkg_norm = pkg.replace('_', '-').lower()
            pkg_key_norm = pkg_key.replace('_', '-').lower()
            if pkg_key_norm == pkg_norm or pkg_key_norm.startswith(pkg_norm + '-'):
                pkg_key = pkg
                break

        reason_chain = get_reason_chain(pkg_key, reasons)
        print(f'  - {rel_path}')
        print(f'    {bold("Reason:")} {reason_chain}')
        print('--------------------------------------------------------')

    try:
        # Force prompt flush before requesting raw input
        print('Do you want to proceed with this refresh? [y/N]: ', end='', flush=True)
        response = input().strip().lower()
        if response not in ('y', 'yes'):
            print('\nRefresh aborted by user.')
            sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print('\n\nRefresh aborted.')
        sys.exit(1)

    print('\n>>> Removing directories...')
    for path in paths_to_delete:
        try:
            rel_path = path.relative_to(project_dir)
        except ValueError:
            rel_path = path
        print(f'    Removing: {rel_path}')
        remove_directory(path)

    print('\nSurgical package reset complete.')


if __name__ == '__main__':
    main()
