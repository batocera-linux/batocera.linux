#!/usr/bin/env python3
import os
import re
import subprocess
import argparse
import sys
import shutil
import stat
from pathlib import Path

# Clean ANSI coloring helper
def bold(text): return f"\033[1m{text}\033[0m"
def yellow(text): return f"\033[93m{text}\033[0m"
def red(text): return f"\033[91m{text}\033[0m"

def find_all_mk_files(project_dir):
    search_dirs = [
        "package/batocera",
        "buildroot/arch",
        "buildroot/boot",
        "buildroot/linux",
        "buildroot/package",
        "buildroot/toolchain"
    ]
    mk_files = {}
    for d in search_dirs:
        full_dir = Path(project_dir) / d
        if full_dir.is_dir():
            for p in full_dir.rglob("*.mk"):
                # Exclude internal buildroot infrastructure files
                if p.name.startswith("pkg-") or p.name in ("Makefile.in", "Makefile", "sdk.mk"):
                    continue
                pkg_name = p.stem
                mk_files[pkg_name] = p
    return mk_files

def clean_tokens(tokens):
    """Filters out GNU Make variables, conditions, and invalid package names."""
    valid_pattern = re.compile(r'^[a-zA-Z0-9\-_]+$')
    return [t.strip() for t in tokens if valid_pattern.match(t.strip())]

def parse_mk_dependencies(all_mk_files):
    dependencies = {}
    provides_map = {}
    kernel_modules = []
    
    # Matches $(eval $(kernel-module))
    kernel_module_regex = re.compile(r'\$\(\s*eval\s*\$\(\s*kernel-module\s*\)\s*\)')

    for pkg_name, path in all_mk_files.items():
        try:
            content = path.read_text(errors='ignore')
        except Exception:
            continue

        if kernel_module_regex.search(content):
            kernel_modules.append(pkg_name)

        # Normalize line continuations (\ followed by newline)
        content = re.sub(r'\\\s*\n', ' ', content)
        lines = content.split('\n')

        pkg_upper = pkg_name.upper().replace('-', '_')
        target_dep_var = f"{pkg_upper}_DEPENDENCIES"
        host_dep_var = f"HOST_{pkg_upper}_DEPENDENCIES"
        target_provides_var = f"{pkg_upper}_PROVIDES"
        host_provides_var = f"HOST_{pkg_upper}_PROVIDES"

        target_dep_regex = re.compile(rf'^\s*{target_dep_var}\s*(?:\+?=|=)\s*(.*)$')
        host_dep_regex = re.compile(rf'^\s*{host_dep_var}\s*(?:\+?=|=)\s*(.*)$')
        target_prov_regex = re.compile(rf'^\s*{target_provides_var}\s*(?:\+?=|=)\s*(.*)$')
        host_prov_regex = re.compile(rf'^\s*{host_provides_var}\s*(?:\+?=|=)\s*(.*)$')

        target_deps = []
        host_deps = []
        target_provides = []
        host_provides = []

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
            dependencies[f"host-{pkg_name}"] = list(set(host_deps))

        if target_provides:
            provides_map[pkg_name] = list(set(target_provides))
        if host_provides:
            provides_map[f"host-{pkg_name}"] = list(set(host_provides))

    return dependencies, provides_map, kernel_modules

def find_package_for_file(changed_file_path, all_mk_files, project_dir):
    """Maps a changed file path back to its parent package using a strict subdirectory descendant check."""
    changed_path = (Path(project_dir) / changed_file_path).resolve()
    
    best_pkg = None
    best_prefix_len = -1
    
    for pkg_name, mk_path in all_mk_files.items():
        pkg_dir = (Path(project_dir) / mk_path).parent.resolve()
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

def get_git_modified_packages(project_dir, days, all_mk_files):
    modified_pkgs = set()
    
    # Check main repository
    try:
        cmd = ["git", "-C", str(project_dir), "log", f'--since={days} days ago', "--name-only", "--format=%n"]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, universal_newlines=True)
        for line in out.splitlines():
            line = line.strip()
            if line:
                pkg = find_package_for_file(line, all_mk_files, project_dir)
                if pkg:
                    modified_pkgs.add(pkg)
    except subprocess.CalledProcessError:
        pass

    # Check Buildroot submodule
    buildroot_dir = Path(project_dir) / "buildroot"
    if buildroot_dir.is_dir():
        try:
            cmd = ["git", "-C", str(buildroot_dir), "log", f'--since={days} days ago', "--name-only", "--format=%n"]
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, universal_newlines=True)
            for line in out.splitlines():
                line = line.strip()
                if line:
                    full_line_path = Path("buildroot") / line
                    pkg = find_package_for_file(full_line_path, all_mk_files, project_dir)
                    if pkg:
                        modified_pkgs.add(pkg)
        except subprocess.CalledProcessError:
            pass

    return modified_pkgs

def filter_built_packages(packages, output_dir):
    build_dir = Path(output_dir) / "build"
    per_package_dir = Path(output_dir) / "per-package"
    
    built_pkgs = set()
    
    build_subdirs = []
    if build_dir.is_dir():
        build_subdirs = [d.name for d in build_dir.iterdir() if d.is_dir()]
        
    per_package_subdirs = set()
    if per_package_dir.is_dir():
        per_package_subdirs = {d.name for d in per_package_dir.iterdir() if d.is_dir()}
        
    for pkg in packages:
        if pkg in per_package_subdirs:
            built_pkgs.add(pkg)
            continue
        for d in build_subdirs:
            if d == pkg or d.startswith(pkg + "-"):
                built_pkgs.add(pkg)
                break
                
    return built_pkgs

def collect_paths_to_delete(packages, output_dir):
    build_dir = Path(output_dir) / "build"
    per_package_dir = Path(output_dir) / "per-package"
    
    paths_to_delete = []
    
    if per_package_dir.is_dir():
        for pkg in packages:
            p_path = per_package_dir / pkg
            if p_path.is_dir():
                paths_to_delete.append(p_path)
                
    if build_dir.is_dir():
        try:
            subdirs = [d for d in build_dir.iterdir() if d.is_dir()]
        except Exception:
            subdirs = []
            
        for pkg in packages:
            for d in subdirs:
                if d.name == pkg or d.name.startswith(pkg + "-"):
                    paths_to_delete.append(d)
                    
    return sorted(list(set(paths_to_delete)))

def remove_directory(path):
    def handle_remove_readonly(func, p, exc_info):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            pass

    try:
        shutil.rmtree(path, onerror=handle_remove_readonly)
    except Exception as e:
        print(f"Error removing {path}: {e}", file=sys.stderr)

def get_reason_chain(pkg, reasons):
    chain = []
    curr = pkg
    while curr in reasons:
        parent = reasons[curr]
        if parent in ("git-modified", "mandatory", "provider-expansion", "kernel-module", "co-located-host"):
            chain.append(f"{curr} ({parent})")
            break
        else:
            chain.append(curr)
            curr = parent
    return " -> ".join(chain)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--mandatory", default="")
    args = parser.parse_args()

    project_dir = Path(args.project_dir)

    print(">>> Scanning workspace for package definitions...")
    all_mk_files = find_all_mk_files(project_dir)
    print(f"    Found {len(all_mk_files)} package definitions.")

    print(f"\n>>> Parsing dependencies and building reverse dependency graph...")
    dependencies, provides_map, kernel_modules = parse_mk_dependencies(all_mk_files)

    print(f"\n>>> Detecting packages modified in git over the last {args.days} days...")
    modified = get_git_modified_packages(project_dir, args.days, all_mk_files)
    if modified:
        for m in sorted(modified):
            print(f"      - {m}")
    else:
        print("      (None detected)")

    mandatory = set(args.mandatory.split())
    if mandatory:
        print("\n>>> Mandatory rebuild packages:")
        for m in sorted(mandatory):
            print(f"      - {m}")

    seed_packages = modified.union(mandatory)
    if not seed_packages:
        print("\nNo seed packages found to reset. Aborting.")
        sys.exit(0)

    # Dictionary to store the structural reason/parent chain for each reset package
    reasons = {}
    for pkg in modified:
        reasons[pkg] = "git-modified"
    for pkg in mandatory:
        if pkg not in reasons:
            reasons[pkg] = "mandatory"

    # Provider/Virtual package expansion
    provider_expansion = set()
    for pkg in seed_packages:
        if pkg in provides_map:
            provider_expansion.update(provides_map[pkg])
    if provider_expansion:
        print("\n>>> Expanding virtual package providers:")
        for p in sorted(provider_expansion):
            print(f"      - {p}")
            if p not in reasons:
                reasons[p] = "provider-expansion"
        seed_packages.update(provider_expansion)

    # Host Co-location check for seed packages
    # If a seed target package has a matching host variant built on disk, include it.
    host_seeds = set()
    host_candidates = [f"host-{pkg}" for pkg in seed_packages if not pkg.startswith("host-")]
    built_host_packages = filter_built_packages(host_candidates, args.output_dir)
    for host_pkg in built_host_packages:
        host_seeds.add(host_pkg)
        if host_pkg not in reasons:
            reasons[host_pkg] = "co-located-host"
    if host_seeds:
        print("\n>>> Co-locating host equivalents for modified packages:")
        for h in sorted(host_seeds):
            print(f"      - {h}")
        seed_packages.update(host_seeds)

    # Build Reverse Dependency Graph
    reverse_deps = {}
    for pkg, deps in dependencies.items():
        for dep in deps:
            reverse_deps.setdefault(dep, []).append(pkg)

    # Recursive graph traversal (BFS) to find affected dependents
    to_reset = set(seed_packages)
    queue = list(seed_packages)

    def add_to_reset(pkg, parent):
        if pkg not in to_reset:
            to_reset.add(pkg)
            queue.append(pkg)
            reasons[pkg] = parent
            
            # HOOK: If 'linux' or 'linux-headers' is pulled in at any point,
            # we also pull in all out-of-tree kernel modules.
            if pkg in ("linux", "linux-headers"):
                for km in kernel_modules:
                    add_to_reset(km, "kernel-module")

    # Trigger kernel module hook immediately if linux starts in the seed set
    if "linux" in to_reset or "linux-headers" in to_reset:
        for km in kernel_modules:
            add_to_reset(km, "kernel-module")

    while queue:
        current = queue.pop(0)
        for rdep in reverse_deps.get(current, []):
            add_to_reset(rdep, current)

    # Filter built packages
    final_packages = filter_built_packages(to_reset, args.output_dir)
    if not final_packages:
        print("\nNo active build outputs found on disk matching the affected packages. Nothing to reset.")
        sys.exit(0)

    # CASCADE PROTECTION: Check if deletion plan size is large
    if len(final_packages) > 30:
        print("\n" + yellow("========================================================"))
        print(yellow("⚠️  WARNING: LARGE DEPENDENCY CASCADE DETECTED"))
        print(yellow("========================================================"))
        print(f"A total of {bold(len(final_packages))} active packages will be reset and rebuilt.")
        print("This is usually triggered by modifications to low-level/core system libraries (such as mesa3d or udev).")
        print("--------------------------------------------------------")
        try:
            response = input("Would you like to perform a " + bold("Shallow Refresh") + " instead?\n(Only resets modified seeds, skipping recursive dependents) [y/N]: ").strip().lower()
            if response in ('y', 'yes'):
                print("\n>>> Downgrading to Shallow Refresh...")
                to_reset = seed_packages
                final_packages = filter_built_packages(to_reset, args.output_dir)
        except (KeyboardInterrupt, EOFError):
            print("\n\nRefresh aborted.")
            sys.exit(1)

    paths_to_delete = collect_paths_to_delete(final_packages, args.output_dir)

    print("\n========================================================")
    print("Surgical Refresh Deletion Plan")
    print("========================================================")
    print("The following directories will be permanently deleted:")
    
    # Track output directory names for cleaner reason mapping
    for path in paths_to_delete:
        try:
            rel_path = path.relative_to(project_dir)
        except ValueError:
            rel_path = path
            
        pkg_key = path.name
        # Match built package format (e.g. 'sdl3-3.4.2' -> 'sdl3')
        for pkg in final_packages:
            if pkg_key == pkg or pkg_key.startswith(pkg + "-"):
                pkg_key = pkg
                break
                
        reason_chain = get_reason_chain(pkg_key, reasons)
        print(f"  - {rel_path}")
        print(f"    {bold('Reason:')} {reason_chain}")
        print("--------------------------------------------------------")

    try:
        response = input("Do you want to proceed with this refresh? [y/N]: ").strip().lower()
        if response not in ('y', 'yes'):
            print("\nRefresh aborted by user.")
            sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\n\nRefresh aborted.")
        sys.exit(1)

    print("\n>>> Removing directories...")
    for path in paths_to_delete:
        try:
            rel_path = path.relative_to(project_dir)
        except ValueError:
            rel_path = path
        print(f"    Removing: {rel_path}")
        remove_directory(path)

    print("\nSurgical package reset complete.")

if __name__ == "__main__":
    main()
