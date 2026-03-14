################################################################################
#
# uboot-powkiddy-x55
#
################################################################################

UBOOT_POWKIDDY_X55_VERSION = 2025.10
UBOOT_POWKIDDY_X55_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_POWKIDDY_X55_SOURCE = u-boot-$(UBOOT_POWKIDDY_X55_VERSION).tar.bz2
UBOOT_POWKIDDY_X55_LICENSE = GPL-2.0+
UBOOT_POWKIDDY_X55_LICENSE_FILES = Licenses/README
UBOOT_POWKIDDY_X55_INSTALL_IMAGES = YES

UBOOT_POWKIDDY_X55_RKBIN_COMMIT = 74213af1e952c4683d2e35952507133b61394862
UBOOT_POWKIDDY_X55_EXTRA_DOWNLOADS = \
    https://github.com/rockchip-linux/rkbin/archive/$(UBOOT_POWKIDDY_X55_RKBIN_COMMIT)/rkbin-$(UBOOT_POWKIDDY_X55_RKBIN_COMMIT).tar.gz

UBOOT_POWKIDDY_X55_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex
UBOOT_POWKIDDY_X55_DEPENDENCIES += host-python-setuptools host-dtc host-swig
UBOOT_POWKIDDY_X55_DEPENDENCIES += host-gnutls host-python-pyelftools

define UBOOT_POWKIDDY_X55_EXTRACT_RKBIN
    mkdir -p $(@D)/rkbin
    $(TAR) -xf $(UBOOT_POWKIDDY_X55_DL_DIR)/rkbin-$(UBOOT_POWKIDDY_X55_RKBIN_COMMIT).tar.gz \
        -C $(@D)/rkbin --strip-components=1
endef
UBOOT_POWKIDDY_X55_POST_EXTRACT_HOOKS += UBOOT_POWKIDDY_X55_EXTRACT_RKBIN

UBOOT_POWKIDDY_X55_MAKE_OPTS = \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)" \
    BL31=$(@D)/rkbin/bin/rk35/rk3568_bl31_v1.45.elf \
    ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/rk3568_ddr_1056MHz_v1.23.bin

define UBOOT_POWKIDDY_X55_CONFIGURE_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_POWKIDDY_X55_MAKE_OPTS) \
        powkiddy-x55-rk3566_defconfig
endef

define UBOOT_POWKIDDY_X55_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_POWKIDDY_X55_MAKE_OPTS)
endef

define UBOOT_POWKIDDY_X55_INSTALL_IMAGES_CMDS
    mkdir -p $(BINARIES_DIR)/uboot-powkiddy-x55
    $(INSTALL) -D -m 0644 $(@D)/u-boot-rockchip.bin \
        $(BINARIES_DIR)/uboot-powkiddy-x55/u-boot-rockchip.bin
endef

$(eval $(generic-package))
