#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Copy prebuilt files
mkdir -p "${IMAGES_DIR}/batocera/uboot-rock-3a"
cp "${IMAGES_DIR}/uboot-rock-3a/idbloader.img" "${IMAGES_DIR}/batocera/uboot-rock-3a/"
cp "${IMAGES_DIR}/uboot-rock-3a/u-boot.itb" "${IMAGES_DIR}/batocera/uboot-rock-3a/"
