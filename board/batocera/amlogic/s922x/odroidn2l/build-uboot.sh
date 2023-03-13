#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

make_uboot () {
    board=$1
    build_target=$2

    ## terrible hack / sometimes the EMMC does not initialize. try the boot sequence until it succeeds
    echo 'CONFIG_BOOTCOMMAND="until false; do run distro_bootcmd; sleep 5; done"' >> configs/${build_target}_defconfig

    # Make config
    make mrproper || exit 1
    make "${build_target}_defconfig" || exit 1

    # Build it
    ARCH=aarch64 CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-" make -j$(nproc) || exit 1
    mkdir -p "../../$board" || exit 1

    # Build and put to appropriate place
    pushd amlogic-boot-fip || exit 1
        ./build-fip.sh "$build_target" ../u-boot.bin "../../../$board/" || { popd; exit 1; }
    popd || exit 1
}

# Download U-Boot mainline
uboot="u-boot-2023.01"
wget "https://ftp.denx.de/pub/u-boot/${uboot}.tar.bz2"
tar xf "${uboot}.tar.bz2" || exit 1
pushd "${uboot}" || exit 1
    # Clone LibreElec Amlogic FIP
    git clone --depth 1 https://github.com/LibreELEC/amlogic-boot-fip || exit 1

    # Apply patch sets
    for patch in ${BR2_EXTERNAL_BATOCERA_PATH}/board/batocera/amlogic/s922x/{,odroidn2l/}patches/uboot/*.patch; do
        echo "Applying patch: $patch"
        patch -p1 < "$patch" || exit 1
    done

    make_uboot uboot-odroidn2l odroid-n2l
popd || exit 1
