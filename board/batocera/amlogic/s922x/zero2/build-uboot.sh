#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Download U-Boot mainline
wget "https://ftp.denx.de/pub/u-boot/u-boot-2022.01.tar.bz2"
tar xf u-boot-2022.01.tar.bz2
cd u-boot-2022.01

Apply patches
PATCHES="${BOARD_DIR}/patches/uboot/*.patch"
for patch in $PATCHES
do
echo "Applying patch: $patch"
patch -p1 < $patch
done

# Make config
make radxa-zero2_defconfig

# Build it
ARCH=aarch64 CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-" make -j$(nproc)
mkdir -p ../../uboot-zero2

# Clone LibreElec Amlogic FIP
git clone --depth 1 https://github.com/LibreELEC/amlogic-boot-fip

# Sign U-Boot build with Amlogic process
AMLOGIC_FIP_DIR="amlogic-boot-fip/radxa-zero2"
AMLOGIC_ENCRYPT_BIN="aml_encrypt_g12b"
cp u-boot.bin ${AMLOGIC_FIP_DIR}/bl33.bin
${AMLOGIC_FIP_DIR}/blx_fix.sh ${AMLOGIC_FIP_DIR}/bl30.bin \
  ${AMLOGIC_FIP_DIR}/zero_tmp \
  ${AMLOGIC_FIP_DIR}/bl30_zero.bin \
  ${AMLOGIC_FIP_DIR}/bl301.bin \
  ${AMLOGIC_FIP_DIR}/bl301_zero.bin \
  ${AMLOGIC_FIP_DIR}/bl30_new.bin bl30
${AMLOGIC_FIP_DIR}/blx_fix.sh ${AMLOGIC_FIP_DIR}/bl2.bin \
  ${AMLOGIC_FIP_DIR}/zero_tmp \
  ${AMLOGIC_FIP_DIR}/bl2_zero.bin \
  ${AMLOGIC_FIP_DIR}/acs.bin \
  ${AMLOGIC_FIP_DIR}/bl21_zero.bin \
  ${AMLOGIC_FIP_DIR}/bl2_new.bin bl2
${AMLOGIC_FIP_DIR}/${AMLOGIC_ENCRYPT_BIN} --bl30sig \
  --input ${AMLOGIC_FIP_DIR}/bl30_new.bin \
  --output ${AMLOGIC_FIP_DIR}/bl30_new.bin.g12a.enc \
  --level v3
${AMLOGIC_FIP_DIR}/${AMLOGIC_ENCRYPT_BIN} --bl3sig  \
  --input ${AMLOGIC_FIP_DIR}/bl30_new.bin.g12a.enc \
  --output ${AMLOGIC_FIP_DIR}/bl30_new.bin.enc \
  --level v3 --type bl30
${AMLOGIC_FIP_DIR}/${AMLOGIC_ENCRYPT_BIN} --bl3sig  \
  --input ${AMLOGIC_FIP_DIR}/bl31.img \
  --output ${AMLOGIC_FIP_DIR}/bl31.img.enc \
  --level v3 --type bl31
${AMLOGIC_FIP_DIR}/${AMLOGIC_ENCRYPT_BIN} --bl3sig  \
  --input ${AMLOGIC_FIP_DIR}/bl33.bin --compress lz4 \
  --output ${AMLOGIC_FIP_DIR}/bl33.bin.enc \
  --level v3 --type bl33 --compress lz4
${AMLOGIC_FIP_DIR}/${AMLOGIC_ENCRYPT_BIN} --bl2sig  \
  --input ${AMLOGIC_FIP_DIR}/bl2_new.bin \
  --output ${AMLOGIC_FIP_DIR}/bl2.n.bin.sig
${AMLOGIC_FIP_DIR}/${AMLOGIC_ENCRYPT_BIN} --bootmk \
   --output ${AMLOGIC_FIP_DIR}/u-boot.bin \
   --bl2 ${AMLOGIC_FIP_DIR}/bl2.n.bin.sig \
   --bl30 ${AMLOGIC_FIP_DIR}/bl30_new.bin.enc \
   --bl31 ${AMLOGIC_FIP_DIR}/bl31.img.enc \
   --bl33 ${AMLOGIC_FIP_DIR}/bl33.bin.enc \
   --ddrfw1 ${AMLOGIC_FIP_DIR}/ddr4_1d.fw \
   --ddrfw2 ${AMLOGIC_FIP_DIR}/ddr4_2d.fw \
   --ddrfw3 ${AMLOGIC_FIP_DIR}/ddr3_1d.fw \
   --ddrfw4 ${AMLOGIC_FIP_DIR}/piei.fw \
   --ddrfw5 ${AMLOGIC_FIP_DIR}/lpddr4_1d.fw \
   --ddrfw6 ${AMLOGIC_FIP_DIR}/lpddr4_2d.fw \
   --ddrfw7 ${AMLOGIC_FIP_DIR}/diag_lpddr4.fw \
   --ddrfw8 ${AMLOGIC_FIP_DIR}/aml_ddr.fw \
   --ddrfw9 ${AMLOGIC_FIP_DIR}/lpddr3_1d.fw \
   --level v3

# Copy to appropriate place
cp ${AMLOGIC_FIP_DIR}/u-boot.bin ../../uboot-zero2/

