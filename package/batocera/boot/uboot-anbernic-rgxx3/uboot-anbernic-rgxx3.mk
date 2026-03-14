################################################################################
#
# uboot-anbernic-rgxx3
#
################################################################################

UBOOT_ANBERNIC_RGXX3_VERSION = 2025.10
UBOOT_ANBERNIC_RGXX3_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_ANBERNIC_RGXX3_SOURCE = u-boot-$(UBOOT_ANBERNIC_RGXX3_VERSION).tar.bz2
UBOOT_ANBERNIC_RGXX3_LICENSE = GPL-2.0+
UBOOT_ANBERNIC_RGXX3_LICENSE_FILES = Licenses/README
UBOOT_ANBERNIC_RGXX3_INSTALL_IMAGES = YES

UBOOT_ANBERNIC_RGXX3_RKBIN_COMMIT = 74213af1e952c4683d2e35952507133b61394862
UBOOT_ANBERNIC_RGXX3_RKBIN_URL = \
    https://github.com/rockchip-linux/rkbin/archive/$(UBOOT_ANBERNIC_RGXX3_RKBIN_COMMIT)
UBOOT_ANBERNIC_RGXX3_EXTRA_DOWNLOADS = \
    $(UBOOT_ANBERNIC_RGXX3_RKBIN_URL)/rkbin-$(UBOOT_ANBERNIC_RGXX3_RKBIN_COMMIT).tar.gz

UBOOT_ANBERNIC_RGXX3_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex
UBOOT_ANBERNIC_RGXX3_DEPENDENCIES += host-python-setuptools host-dtc host-swig
UBOOT_ANBERNIC_RGXX3_DEPENDENCIES += host-gnutls host-python-pyelftools

define UBOOT_ANBERNIC_RGXX3_EXTRACT_RKBIN
    mkdir -p $(@D)/rkbin
    $(TAR) -xf $(UBOOT_ANBERNIC_RGXX3_DL_DIR)/rkbin-$(UBOOT_ANBERNIC_RGXX3_RKBIN_COMMIT).tar.gz \
        -C $(@D)/rkbin --strip-components=1
endef
UBOOT_ANBERNIC_RGXX3_POST_EXTRACT_HOOKS += UBOOT_ANBERNIC_RGXX3_EXTRACT_RKBIN

UBOOT_ANBERNIC_RGXX3_MAKE_OPTS = \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)" \
    BL31=$(@D)/rkbin/bin/rk35/rk3568_bl31_v1.45.elf \
    ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/rk3568_ddr_1056MHz_v1.23.bin

define UBOOT_ANBERNIC_RGXX3_CONFIGURE_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ANBERNIC_RGXX3_MAKE_OPTS) \
        anbernic-rgxx3-rk3566_defconfig
endef

define UBOOT_ANBERNIC_RGXX3_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ANBERNIC_RGXX3_MAKE_OPTS)
endef

define UBOOT_ANBERNIC_RGXX3_INSTALL_IMAGES_CMDS
    mkdir -p $(BINARIES_DIR)/uboot-anbernic-rgxx3
    $(INSTALL) -D -m 0644 $(@D)/u-boot-rockchip.bin \
        $(BINARIES_DIR)/uboot-anbernic-rgxx3/u-boot-rockchip.bin
endef

$(eval $(generic-package))
