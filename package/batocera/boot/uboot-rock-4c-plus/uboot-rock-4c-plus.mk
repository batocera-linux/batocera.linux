################################################################################
#
# uboot-rock-4c-plus
#
################################################################################

UBOOT_ROCK_4C_PLUS_VERSION = 2026.04
UBOOT_ROCK_4C_PLUS_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_ROCK_4C_PLUS_SOURCE = u-boot-$(UBOOT_ROCK_4C_PLUS_VERSION).tar.bz2
UBOOT_ROCK_4C_PLUS_LICENSE = GPL-2.0+
UBOOT_ROCK_4C_PLUS_LICENSE_FILES = Licenses/README
UBOOT_ROCK_4C_PLUS_INSTALL_IMAGES = YES

UBOOT_ROCK_4C_PLUS_DEPENDENCIES = arm-trusted-firmware host-pkgconf \
	host-openssl host-bison host-flex host-python-setuptools host-dtc \
	host-swig host-gnutls host-python-pyelftools

UBOOT_ROCK_4C_PLUS_MAKE_OPTS = \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	HOSTCC="$(HOSTCC)" \
	HOSTCFLAGS="$(HOST_CFLAGS)" \
	HOSTLDFLAGS="$(HOST_LDFLAGS)" \
	BL31=$(BINARIES_DIR)/bl31.elf

define UBOOT_ROCK_4C_PLUS_CONFIGURE_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ROCK_4C_PLUS_MAKE_OPTS) \
		rock-4c-plus-rk3399_defconfig
endef

define UBOOT_ROCK_4C_PLUS_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_ROCK_4C_PLUS_MAKE_OPTS)
endef

define UBOOT_ROCK_4C_PLUS_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/uboot-rock-4c-plus
	rm -f $(BINARIES_DIR)/uboot-rock-4c-plus/uboot.img \
		$(BINARIES_DIR)/uboot-rock-4c-plus/trust.img
	$(INSTALL) -D -m 0644 $(@D)/idbloader.img \
		$(BINARIES_DIR)/uboot-rock-4c-plus/idbloader.img
	$(INSTALL) -D -m 0644 $(@D)/u-boot.itb \
		$(BINARIES_DIR)/uboot-rock-4c-plus/u-boot.itb
endef

$(eval $(generic-package))
