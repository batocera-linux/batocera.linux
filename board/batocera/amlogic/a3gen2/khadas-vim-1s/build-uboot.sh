#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Just copy working blob until better solution
mkdir -p ../uboot-vim1s
cp "${IMAGES_DIR}/uboot-vim1s/u-boot.bin.sd.signed" ../uboot-vim1s/
