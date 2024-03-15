#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Copy prebuilt files
mkdir -p "${IMAGES_DIR}/batocera/uboot-rock-3c"
cp "${IMAGES_DIR}/uboot-rock-3c/idbloader.img" "${IMAGES_DIR}/batocera/uboot-rock-3c/"
cp "${IMAGES_DIR}/uboot-rock-3c/u-boot.itb" "${IMAGES_DIR}/batocera/uboot-rock-3c/"
