#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Download U-Boot mainline
wget -O u-boot-2026.10.tar.gz "https://github.com/u-boot/u-boot/archive/refs/tags/v2026.10.tar.gz"
tar xf u-boot-2026.10.tar.gz
cd u-boot-2026.10

# Apply patches
PATCHES="${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/amlogic/s9gen4/patches/uboot/*.patch"
for patch in $PATCHES
do
echo "Applying patch: $patch"
patch -p1 < $patch
done

# Make config
make khadas-vim1s_defconfig

# Build it
ARCH=aarch64 CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-" make -j$(nproc)
mkdir -p ../../uboot-vim1s

# LibreELEC Amlogic FIP
FIP_VERSION=b6600f2857fdf81d11f18ea7a2e44aa989e7bcc4
wget -O amlogic-boot-fip.tar.gz "https://github.com/LibreELEC/amlogic-boot-fip/archive/${FIP_VERSION}.tar.gz"
mkdir amlogic-boot-fip
tar xf amlogic-boot-fip.tar.gz -C amlogic-boot-fip --strip-components=1

# pack-s4.sh needs xxd -r -p and openssl, neither is in the build image
mkdir -p fip-bin
cat > fip-bin/xxd << 'EOF'
#!/usr/bin/env python3
import sys
sys.stdout.buffer.write(bytes.fromhex("".join(sys.stdin.read().split())))
EOF
chmod +x fip-bin/xxd
export PATH="${PWD}/fip-bin:${PATH}:${HOST_DIR}/bin"

# Build and put to appropriate place
cd amlogic-boot-fip && ./build-fip.sh khadas-vim1s ../u-boot.bin ../../../uboot-vim1s/
