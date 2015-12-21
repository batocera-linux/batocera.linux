#!/bin/bash -e

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

RECALBOX_BINARIES_DIR="${BINARIES_DIR}/recalbox"
RECALBOX_TARGET_DIR="${TARGET_DIR}/recalbox"
RECALBOX_HOME_PWD="${PWD}/board/recalbox/share/system"
RECALBOX_SSH_PWD="${RECALBOX_HOME_PWD}/.ssh"
RECALBOX_SSH_AUTHORIZED_KEY_PWD="${RECALBOX_SSH_PWD}/authorized_keys"

sed -i "s|root:x:0:0:root:/root:/bin/sh|root:x:0:0:root:/recalbox/share/system:/bin/sh|g" "${TARGET_DIR}/etc/passwd"
rm -rf "${TARGET_DIR}/etc/dropbear"
ln -s "/recalbox/share/system/ssh" "${TARGET_DIR}/etc/dropbear"
chmod -R go-w "${RECALBOX_HOME_PWD}"
mkdir -p "${RECALBOX_SSH_PWD}"
chmod 0700 "${RECALBOX_SSH_PWD}"
touch "${RECALBOX_SSH_AUTHORIZED_KEY_PWD}"
chmod 0600 "${RECALBOX_SSH_AUTHORIZED_KEY_PWD}"
