#!/bin/bash

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

rm "${BINARIES_DIR}/modules"
rm "${BINARIES_DIR}/rootfs.tar"
"${HOST_DIR}/bin/mksquashfs" "${TARGET_DIR}/lib/modules/" "${BINARIES_DIR}/modules" -comp zstd
(cd "${BINARIES_DIR}" && tar cf - * | gzip > "${BINARIES_DIR}/kernel.tar.gz")
