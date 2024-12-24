#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Copy prebuilt files
mkdir -p "${IMAGES_DIR}/batocera/uboot-orangepi-3b"
cp "${IMAGES_DIR}/uboot-orangepi-3b/idbloader.img" "${IMAGES_DIR}/batocera/uboot-orangepi-3b/"
cp "${IMAGES_DIR}/uboot-orangepi-3b/u-boot.itb" "${IMAGES_DIR}/batocera/uboot-orangepi-3b/"
