################################################################################
#
# uboot-rk3576
#
################################################################################

UBOOT_RK3576_VERSION = 2026.04
UBOOT_RK3576_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_RK3576_SOURCE = u-boot-$(UBOOT_RK3576_VERSION).tar.bz2
UBOOT_RK3576_LICENSE = GPL-2.0+
UBOOT_RK3576_LICENSE_FILES = Licenses/README
UBOOT_RK3576_INSTALL_IMAGES = YES

# Rockchip binary blobs for DDR init and ATF (BL31)
UBOOT_RK3576_RKBIN_COMMIT = 74213af1e952c4683d2e35952507133b61394862
UBOOT_RK3576_RKBIN_URL = \
    https://github.com/rockchip-linux/rkbin/archive/$(UBOOT_RK3576_RKBIN_COMMIT)
UBOOT_RK3576_EXTRA_DOWNLOADS = \
    $(UBOOT_RK3576_RKBIN_URL)/rkbin-$(UBOOT_RK3576_RKBIN_COMMIT).tar.gz

UBOOT_RK3576_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex
UBOOT_RK3576_DEPENDENCIES += host-python-setuptools host-dtc host-swig
UBOOT_RK3576_DEPENDENCIES += host-gnutls host-python-pyelftools

define UBOOT_RK3576_EXTRACT_RKBIN
    mkdir -p $(@D)/rkbin
    $(TAR) -xf $(UBOOT_RK3576_DL_DIR)/rkbin-$(UBOOT_RK3576_RKBIN_COMMIT).tar.gz \
        -C $(@D)/rkbin --strip-components=1
endef
UBOOT_RK3576_POST_EXTRACT_HOOKS += UBOOT_RK3576_EXTRACT_RKBIN

UBOOT_RK3576_MAKE_OPTS = \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCC="$(HOSTCC)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)" \
    BL31=$(@D)/rkbin/bin/rk35/rk3576_bl31_v1.20.elf \
    ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/rk3576_ddr_lp4_2112MHz_lp5_2736MHz_v1.09.bin

define UBOOT_RK3576_CONFIGURE_CMDS
    # Using quartz64-a-rk3566 as the generic baseline for RK3566/RK3568 devices
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3576_MAKE_OPTS) \
        generic-rk3576_defconfig
endef

define UBOOT_RK3576_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3576_MAKE_OPTS)
endef

define UBOOT_RK3576_INSTALL_IMAGES_CMDS
    mkdir -p $(BINARIES_DIR)/uboot-rk356x
    # u-boot-rockchip.bin contains both the idbloader.img and u-boot.itb
    $(INSTALL) -D -m 0644 $(@D)/u-boot-rockchip.bin \
        $(BINARIES_DIR)/uboot-rk3576/u-boot-rockchip.bin
endef

$(eval $(generic-package))
