################################################################################
#
# uboot files for HardKernel ODROID M1
#
################################################################################

UBOOT_ODROID_M1_VERSION = 2026.04
UBOOT_ODROID_M1_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_ODROID_M1_SOURCE = u-boot-$(UBOOT_ODROID_M1_VERSION).tar.bz2
UBOOT_ODROID_M1_LICENSE = GPL-2.0+
UBOOT_ODROID_M1_LICENSE_FILES = Licenses/README
UBOOT_ODROID_M1_INSTALL_IMAGES = YES

# Rockchip binary blobs for DDR init and ATF (BL31)
UBOOT_ODROID_M1_RKBIN_COMMIT = 74213af1e952c4683d2e35952507133b61394862
UBOOT_ODROID_M1_RKBIN_URL = \
    https://github.com/rockchip-linux/rkbin/archive/$(UBOOT_ODROID_M1_RKBIN_COMMIT)
UBOOT_ODROID_M1_EXTRA_DOWNLOADS = \
    $(UBOOT_ODROID_M1_RKBIN_URL)/rkbin-$(UBOOT_ODROID_M1_RKBIN_COMMIT).tar.gz

UBOOT_ODROID_M1_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex
UBOOT_ODROID_M1_DEPENDENCIES += host-python-setuptools host-dtc host-swig
UBOOT_ODROID_M1_DEPENDENCIES += host-gnutls host-python-pyelftools

define UBOOT_ODROID_M1_EXTRACT_RKBIN
    mkdir -p $(@D)/rkbin
    $(TAR) -xf $(UBOOT_ODROID_M1_DL_DIR)/rkbin-$(UBOOT_ODROID_M1_RKBIN_COMMIT).tar.gz \
        -C $(@D)/rkbin --strip-components=1
endef
UBOOT_ODROID_M1_POST_EXTRACT_HOOKS += UBOOT_ODROID_M1_EXTRACT_RKBIN

# ROCKCHIP_TPL only ever lands in the SPL-stage artifacts, which are discarded
# here (see INSTALL_IMAGES below). It is passed because the default make target
# still builds them, and it is pinned to the same DDR blob the previously
# shipped prebuilt u-boot.itb was verified with.
UBOOT_ODROID_M1_MAKE_OPTS = \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCC="$(HOSTCC)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)" \
    BL31=$(@D)/rkbin/bin/rk35/rk3568_bl31_v1.45.elf \
    ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/rk3568_ddr_1560MHz_v1.23.bin

# Upstream U-Boot carries a real defconfig for this exact board, used unmodified.
define UBOOT_ODROID_M1_CONFIGURE_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ODROID_M1_MAKE_OPTS) \
        odroid-m1-rk3568_defconfig
endef

define UBOOT_ODROID_M1_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ODROID_M1_MAKE_OPTS)
endef

# Only the main-stage FIT is taken from this build. idbloader.img (SPL) stays
# Hardkernel's own prebuilt blob, committed next to this file: it is the
# stage the boot ROM itself validates, it is proven on this board, and it is
# the one piece whose replacement can leave the board unbootable.
define UBOOT_ODROID_M1_INSTALL_IMAGES_CMDS
    mkdir -p $(BINARIES_DIR)/uboot-odroid-m1
    $(INSTALL) -D -m 0644 $(@D)/u-boot.itb \
        $(BINARIES_DIR)/uboot-odroid-m1/u-boot.itb
    $(INSTALL) -D -m 0644 $(UBOOT_ODROID_M1_PKGDIR)/idbloader.img \
        $(BINARIES_DIR)/uboot-odroid-m1/idbloader.img
endef

$(eval $(generic-package))
