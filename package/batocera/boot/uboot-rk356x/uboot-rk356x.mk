################################################################################
#
# uboot-rk356x
#
################################################################################

UBOOT_RK356X_VERSION = 2026.04
UBOOT_RK356X_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_RK356X_SOURCE = u-boot-$(UBOOT_RK356X_VERSION).tar.bz2
UBOOT_RK356X_LICENSE = GPL-2.0+
UBOOT_RK356X_LICENSE_FILES = Licenses/README
UBOOT_RK356X_INSTALL_IMAGES = YES

# Rockchip binary blobs for DDR init and ATF (BL31)
UBOOT_RK356X_RKBIN_COMMIT = 74213af1e952c4683d2e35952507133b61394862
UBOOT_RK356X_RKBIN_URL = \
    https://github.com/rockchip-linux/rkbin/archive/$(UBOOT_RK356X_RKBIN_COMMIT)
UBOOT_RK356X_EXTRA_DOWNLOADS = \
    $(UBOOT_RK356X_RKBIN_URL)/rkbin-$(UBOOT_RK356X_RKBIN_COMMIT).tar.gz

UBOOT_RK356X_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex
UBOOT_RK356X_DEPENDENCIES += host-python-setuptools host-dtc host-swig
UBOOT_RK356X_DEPENDENCIES += host-gnutls host-python-pyelftools

define UBOOT_RK356X_EXTRACT_RKBIN
    mkdir -p $(@D)/rkbin
    $(TAR) -xf $(UBOOT_RK356X_DL_DIR)/rkbin-$(UBOOT_RK356X_RKBIN_COMMIT).tar.gz \
        -C $(@D)/rkbin --strip-components=1
endef
UBOOT_RK356X_POST_EXTRACT_HOOKS += UBOOT_RK356X_EXTRACT_RKBIN

UBOOT_RK356X_MAKE_OPTS = \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCC="$(HOSTCC)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)" \
    BL31=$(@D)/rkbin/bin/rk35/rk3568_bl31_v1.45.elf \
    ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/rk3568_ddr_1056MHz_v1.23.bin

define UBOOT_RK356X_CONFIGURE_CMDS
    # Using quartz64-a-rk3566 as the generic baseline for RK3566/RK3568 devices
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK356X_MAKE_OPTS) \
        quartz64-a-rk3566_defconfig
endef

define UBOOT_RK356X_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK356X_MAKE_OPTS)
endef

define UBOOT_RK356X_INSTALL_IMAGES_CMDS
    mkdir -p $(BINARIES_DIR)/uboot-rk356x
    # u-boot-rockchip.bin contains both the idbloader.img and u-boot.itb
    $(INSTALL) -D -m 0644 $(@D)/u-boot-rockchip.bin \
        $(BINARIES_DIR)/uboot-rk356x/u-boot-rockchip.bin
endef

$(eval $(generic-package))

