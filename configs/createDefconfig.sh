#!/bin/bash

set -euo pipefail

readonly board_file="$1"
readonly user_defconfig_file="$2"
readonly defconfig_file="$3"

if [[ ! -e "${board_file}" ]]; then
    echo "file ${board_file} not found" >&2
    exit 1
fi

if [[ ! -e "${user_defconfig_file}" ]]; then
    echo "file ${user_defconfig_file} not found" >&2
    exit 1
fi

readonly config_dir="$(dirname "${board_file}")"

readonly tmpl0="${defconfig_file}.tmpl0"
readonly tmpl1="${defconfig_file}.tmpl1"

cleanup() {
    rm -f "${tmpl0}" "${tmpl1}"
}
trap cleanup EXIT

> "${tmpl0}"
> "${tmpl1}"

# Include only if the file exists:
# -include something.local

# Include always:
# include something.local

include_file() {
    local included_file="$1"
    local outfile="$2"

    echo "# from file ${included_file}"  >> "${outfile}"
    cat "${config_dir}/${included_file}" >> "${outfile}"
    echo                                 >> "${outfile}"
}

parse_includes() {
    local infile="$1"
    local outfile="$2"
    local inc x

    while read -r inc x; do
        if [[ "${inc#-}" == "$inc" ]] && [[ ! -f "${config_dir}/${x}" ]]; then
            echo "Error: included file ${x} not found (included from ${infile})" >&2
            exit 1
        fi

        if [[ -f "${config_dir}/${x}" ]]; then
            include_file "${x}" "${outfile}"
        fi
    done < <(grep -E '^-?include ' "${infile}")
}

parse_includes "${board_file}" "${tmpl0}"
parse_includes "${tmpl0}" "${tmpl1}"

strip_includes() {
    grep -vE '^-?include ' "$1" || true
}

{
    strip_includes "${tmpl1}"
    strip_includes "${tmpl0}"
    echo "### from board file ###"
    strip_includes "${board_file}"
    echo
    echo "### from add-defconfig ###"
    strip_includes "${user_defconfig_file}"
} > "${defconfig_file}"
