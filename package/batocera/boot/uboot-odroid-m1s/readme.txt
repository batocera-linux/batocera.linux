Built using buildroot config...

# Odroid-M1S U-Boot
BR2_TARGET_UBOOT=y
BR2_TARGET_UBOOT_BUILD_SYSTEM_KCONFIG=y
BR2_TARGET_UBOOT_CUSTOM_VERSION=y
BR2_TARGET_UBOOT_CUSTOM_GIT=y
BR2_TARGET_UBOOT_CUSTOM_REPO_URL="https://github.com/Kwiboo/u-boot-rockchip"
BR2_TARGET_UBOOT_CUSTOM_REPO_VERSION="rk3xxx-2024.07"
BR2_TARGET_UBOOT_BOARD_DEFCONFIG="odroid-m1s-rk3566"
BR2_TARGET_UBOOT_NEEDS_PYLIBFDT=y
BR2_TARGET_UBOOT_NEEDS_OPENSSL=y
BR2_TARGET_UBOOT_NEEDS_PYELFTOOLS=y
BR2_TARGET_UBOOT_NEEDS_ROCKCHIP_RKBIN=y
BR2_PACKAGE_HOST_UBOOT_TOOLS_FIT_SUPPORT=y
BR2_PACKAGE_HOST_DOSFSTOOLS=y
BR2_PACKAGE_HOST_DTC=y
BR2_PACKAGE_HOST_GENIMAGE=y
BR2_PACKAGE_HOST_MTOOLS=y
BR2_PACKAGE_HOST_UBOOT_TOOLS=y
BR2_PACKAGE_ROCKCHIP_RKBIN=y
BR2_PACKAGE_ROCKCHIP_RKBIN_TPL_FILENAME="bin/rk35/rk3566_ddr_1056MHz_v1.21.bin"
BR2_PACKAGE_ROCKCHIP_RKBIN_BL31_FILENAME="bin/rk35/rk3568_bl31_v1.44.elf"

rockchip-rkbin commit a2a0b89b6c8c612dca5ed9ed8a68db8a07f68bc0
