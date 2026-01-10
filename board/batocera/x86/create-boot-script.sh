#!/bin/bash

# HOST_DIR = host dir
# BOARD_DIR = board specific dir
# BUILD_DIR = base dir/build
# BINARIES_DIR = images dir
# TARGET_DIR = target dir
# BATOCERA_BINARIES_DIR = batocera binaries sub directory

HOST_DIR=$1
BOARD_DIR=$2
BUILD_DIR=$3
BINARIES_DIR=$4
TARGET_DIR=$5
BATOCERA_BINARIES_DIR=$6

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot/syslinux" || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT"      || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera"  || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/grub"          || exit 1

# Batocera kernel, initrd, and root
cp "${BINARIES_DIR}/bzImage"         "${BATOCERA_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/initrd.gz"       "${BATOCERA_BINARIES_DIR}/boot/boot/"                || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/rufomaculata"    "${BATOCERA_BINARIES_DIR}/boot/boot/rufomaculata.update" || exit 1

# Legacy bootloader (vestigial)
cp "${BOARD_DIR}/boot/syslinux.cfg"       "${BATOCERA_BINARIES_DIR}/boot/boot/"          || exit 1

# Legacy bootloader
cp "${BOARD_DIR}/boot/syslinux.cfg"       "${BATOCERA_BINARIES_DIR}/boot/boot/syslinux/" || exit 1
cp "${BINARIES_DIR}/syslinux/menu.c32"    "${BATOCERA_BINARIES_DIR}/boot/boot/syslinux/" || exit 1
cp "${BINARIES_DIR}/syslinux/libutil.c32" "${BATOCERA_BINARIES_DIR}/boot/boot/syslinux/" || exit 1

# Syslinux EFI loader with Batocera boot configuration
cp "${BOARD_DIR}/boot/syslinux.cfg"             "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/"             || exit 1
cp "${BINARIES_DIR}/syslinux/efi64/menu.c32"    "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/"             || exit 1
cp "${BINARIES_DIR}/syslinux/efi64/libutil.c32" "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/"             || exit 1
cp "${BINARIES_DIR}/syslinux/ldlinux.e32"       "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/"             || exit 1
cp "${BINARIES_DIR}/syslinux/ldlinux.e64"       "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/"             || exit 1
cp "${BINARIES_DIR}/syslinux/bootx64.efi"       "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/grubx64.efi"  || exit 1
cp "${BINARIES_DIR}/syslinux/batocera-mok.cer"  "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/"             || exit 1
cp "${BINARIES_DIR}/shim-signed/shimx64.efi"    "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/"             || exit 1
cp "${BINARIES_DIR}/shim-signed/shimx64.efi"    "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/bootx64.efi"  || exit 1
cp "${BINARIES_DIR}/shim-signed/mmx64.efi"      "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/"             || exit 1

# grub2 for ia32 x86_64 mixed-mode loading
cp "${BINARIES_DIR}/shim-signed/shimia32.efi"   "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/"             || exit 1
cp "${BINARIES_DIR}/shim-signed/shimia32.efi"   "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/bootia32.efi" || exit 1
cp "${BINARIES_DIR}/shim-signed/mmia32.efi"     "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/"             || exit 1
cp "${BINARIES_DIR}/syslinux/grubia32.efi"      "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/"             || exit 1
cp "${BOARD_DIR}/boot/grub.cfg"                 "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/"                 || exit 1

# EFI boot manager entries to be created by fb*.efi if missing
( printf '\xFF\xFE' ; iconv -t UCS-2 < "${BOARD_DIR}/boot/bootx64.csv" )  > "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/BOOTX64.CSV"  || exit 1
( printf '\xFF\xFE' ; iconv -t UCS-2 < "${BOARD_DIR}/boot/bootia32.csv" ) > "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera/BOOTIA32.CSV" || exit 1

# Fallback boot loader with secure boot shim and Machine Owner Key (MOK) Manager
# https://github.com/rhboot/shim/blob/a1170bb00a116783cc6623b403e785d86b2f97d7/README.fallback
# https://www.rodsbooks.com/efi-bootloaders/fallback.html
cp "${BINARIES_DIR}/shim-signed/shimx64.efi"  "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/BOOTX64.EFI"  || exit 1
cp "${BINARIES_DIR}/shim-signed/mmx64.efi"    "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/"             || exit 1
cp "${BINARIES_DIR}/syslinux/fbx64.efi"       "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/"             || exit 1
cp "${BINARIES_DIR}/shim-signed/shimia32.efi" "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/BOOTIA32.EFI" || exit 1
cp "${BINARIES_DIR}/shim-signed/mmia32.efi"   "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/"             || exit 1
cp "${BINARIES_DIR}/shim-signed/fbia32.efi"   "${BATOCERA_BINARIES_DIR}/boot/EFI/BOOT/"             || exit 1

# Another copy of the MOK cert with a hard-to-miss name at the top level, for ease-of-use
cp "${BINARIES_DIR}/syslinux/batocera-mok.cer"  "${BATOCERA_BINARIES_DIR}/boot/ENROLL_THIS_KEY_IN_MOKMANAGER_batocera.cer" || exit 1

exit 0
