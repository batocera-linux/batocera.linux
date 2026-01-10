################################################################################
#
# uboot-radxa-zero-3
#
################################################################################

UBOOT_RADXA_ZERO_3_VERSION = 2025.10
UBOOT_RADXA_ZERO_3_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_RADXA_ZERO_3_SOURCE = u-boot-$(UBOOT_RADXA_ZERO_3_VERSION).tar.bz2
UBOOT_RADXA_ZERO_3_LICENSE = GPL-2.0+
UBOOT_RADXA_ZERO_3_LICENSE_FILES = Licenses/README
UBOOT_RADXA_ZERO_3_INSTALL_IMAGES = YES

UBOOT_RADXA_ZERO_3_RKBIN_COMMIT = 74213af1e952c4683d2e35952507133b61394862
UBOOT_RADXA_ZERO_3_RKBIN_URL = \
    https://github.com/rockchip-linux/rkbin/archive/$(UBOOT_RADXA_ZERO_3_RKBIN_COMMIT)
UBOOT_RADXA_ZERO_3_EXTRA_DOWNLOADS = \
    $(UBOOT_RADXA_ZERO_3_RKBIN_URL)/rkbin-$(UBOOT_RADXA_ZERO_3_RKBIN_COMMIT).tar.gz

UBOOT_RADXA_ZERO_3_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex
UBOOT_RADXA_ZERO_3_DEPENDENCIES += host-python-setuptools host-dtc host-swig
UBOOT_RADXA_ZERO_3_DEPENDENCIES += host-gnutls host-python-pyelftools

define UBOOT_RADXA_ZERO_3_EXTRACT_RKBIN
    mkdir -p $(@D)/rkbin
    $(TAR) -xf $(UBOOT_RADXA_ZERO_3_DL_DIR)/rkbin-$(UBOOT_RADXA_ZERO_3_RKBIN_COMMIT).tar.gz \
        -C $(@D)/rkbin --strip-components=1
endef
UBOOT_RADXA_ZERO_3_POST_EXTRACT_HOOKS += UBOOT_RADXA_ZERO_3_EXTRACT_RKBIN

UBOOT_RADXA_ZERO_3_MAKE_OPTS = \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)" \
    BL31=$(@D)/rkbin/bin/rk35/rk3568_bl31_v1.45.elf \
    ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/rk3566_ddr_1056MHz_v1.23.bin

define UBOOT_RADXA_ZERO_3_CONFIGURE_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RADXA_ZERO_3_MAKE_OPTS) \
        radxa-zero-3-rk3566_defconfig
endef

define UBOOT_RADXA_ZERO_3_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RADXA_ZERO_3_MAKE_OPTS)
endef

define UBOOT_RADXA_ZERO_3_INSTALL_IMAGES_CMDS
    mkdir -p $(BINARIES_DIR)/uboot-radxa-zero-3
    $(INSTALL) -D -m 0644 $(@D)/u-boot-rockchip.bin \
        $(BINARIES_DIR)/uboot-radxa-zero-3/u-boot-rockchip.bin
endef

$(eval $(generic-package))
