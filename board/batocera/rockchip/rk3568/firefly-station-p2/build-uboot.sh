#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Copy prebuilt files
mkdir -p "${IMAGES_DIR}/batocera/uboot-firefly-station-p2"
cp "${IMAGES_DIR}/uboot-firefly-station-p2/idbloader.img" "${IMAGES_DIR}/batocera/uboot-firefly-station-p2/"
cp "${IMAGES_DIR}/uboot-firefly-station-p2/uboot.img" "${IMAGES_DIR}/batocera/uboot-firefly-station-p2/"
