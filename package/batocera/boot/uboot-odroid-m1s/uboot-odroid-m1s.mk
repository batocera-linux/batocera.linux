################################################################################
#
# uboot-odroid-m1s
#
################################################################################

UBOOT_ODROID_M1S_VERSION = 2025.10
UBOOT_ODROID_M1S_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_ODROID_M1S_SOURCE = u-boot-$(UBOOT_ODROID_M1S_VERSION).tar.bz2
UBOOT_ODROID_M1S_LICENSE = GPL-2.0+
UBOOT_ODROID_M1S_LICENSE_FILES = Licenses/README
UBOOT_ODROID_M1S_INSTALL_IMAGES = YES

UBOOT_ODROID_M1S_RKBIN_COMMIT = 74213af1e952c4683d2e35952507133b61394862
UBOOT_ODROID_M1S_RKBIN_URL = \
    https://github.com/rockchip-linux/rkbin/archive/$(UBOOT_ODROID_M1S_RKBIN_COMMIT)
UBOOT_ODROID_M1S_EXTRA_DOWNLOADS = \
    $(UBOOT_ODROID_M1S_RKBIN_URL)/rkbin-$(UBOOT_ODROID_M1S_RKBIN_COMMIT).tar.gz

UBOOT_ODROID_M1S_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex
UBOOT_ODROID_M1S_DEPENDENCIES += host-python-setuptools host-dtc host-swig
UBOOT_ODROID_M1S_DEPENDENCIES += host-gnutls host-python-pyelftools

define UBOOT_ODROID_M1S_EXTRACT_RKBIN
    mkdir -p $(@D)/rkbin
    $(TAR) -xf $(UBOOT_ODROID_M1S_DL_DIR)/rkbin-$(UBOOT_ODROID_M1S_RKBIN_COMMIT).tar.gz \
        -C $(@D)/rkbin --strip-components=1
endef
UBOOT_ODROID_M1S_POST_EXTRACT_HOOKS += UBOOT_ODROID_M1S_EXTRACT_RKBIN

UBOOT_ODROID_M1S_MAKE_OPTS = \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)" \
    BL31=$(@D)/rkbin/bin/rk35/rk3568_bl31_v1.45.elf \
    ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/rk3568_ddr_1056MHz_v1.23.bin

define UBOOT_ODROID_M1S_CONFIGURE_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ODROID_M1S_MAKE_OPTS) \
        odroid-m1s-rk3566_defconfig
endef

define UBOOT_ODROID_M1S_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ODROID_M1S_MAKE_OPTS)
endef

define UBOOT_ODROID_M1S_INSTALL_IMAGES_CMDS
    mkdir -p $(BINARIES_DIR)/uboot-odroid-m1s
    $(INSTALL) -D -m 0644 $(@D)/u-boot-rockchip.bin \
        $(BINARIES_DIR)/uboot-odroid-m1s/u-boot-rockchip.bin
endef

$(eval $(generic-package))
