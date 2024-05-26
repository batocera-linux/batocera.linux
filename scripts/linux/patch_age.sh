#!/bin/bash

_how_old_helper() {
	f="$1"
	prefix="$2"
	now=$(date +%s)
	file_date=$(git log -1 --date unix --format="%cd" "$f")
	printf "%s\t" "$((($now-$file_date)/60/60/24))"
	printf "%s%s\n" "$prefix" "$f"
}

how_old() { 
	shopt -s globstar nullglob;
	pushd "$(git rev-parse --show-superproject-working-tree --show-toplevel| head -1)" > /dev/null || exit 1
		for f in package/batocera/**/$1/**/*.patch; do
			_how_old_helper "$f"
		done
		for f in board/**/$1/**/*.patch; do
			_how_old_helper "$f"
		done
		pushd buildroot > /dev/null || exit 1
			for f in package/$1/**/*.patch; do
				_how_old_helper "$f" buildroot/
			done
		popd > /dev/null || exit 1
	popd > /dev/null || exit 1
}

how_old "$@"
