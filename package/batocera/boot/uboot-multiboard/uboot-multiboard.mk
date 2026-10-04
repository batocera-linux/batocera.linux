################################################################################
#
# uboot multiboard
#
################################################################################

UBOOT_MULTIBOARD_VERSION = 2026.07
UBOOT_MULTIBOARD_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_MULTIBOARD_SOURCE = u-boot-$(UBOOT_MULTIBOARD_VERSION).tar.bz2
UBOOT_MULTIBOARD_DL_SUBDIR = uboot
UBOOT_MULTIBOARD_LICENSE = GPL-2.0+
UBOOT_MULTIBOARD_LICENSE_FILES = Licenses/README
UBOOT_MULTIBOARD_INSTALL_IMAGES = YES

UBOOT_MULTIBOARD_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex \
	host-python-setuptools host-dtc host-swig host-gnutls host-python-pyelftools \
	host-util-linux

ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_H3),y)
UBOOT_MULTIBOARD_DEPENDENCIES += arm-trusted-firmware
endif

UBOOT_MULTIBOARD_CONFIGS = $(call qstrip,$(BR2_PACKAGE_UBOOT_MULTIBOARD_CONFIGS))
UBOOT_MULTIBOARD_BINARIES = $(call qstrip,$(BR2_PACKAGE_UBOOT_MULTIBOARD_BINARIES))
UBOOT_MULTIBOARD_FRAGMENTS = $(UBOOT_MULTIBOARD_PKGDIR)/uboot.config.fragment

UBOOT_MULTIBOARD_MAKE_OPTS = \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	HOSTCC="$(HOSTCC)" \
	HOSTCFLAGS="$(HOST_CFLAGS)" \
	HOSTLDFLAGS="$(HOST_LDFLAGS)"

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y)
UBOOT_MULTIBOARD_MAKE_OPTS += BL32=$(BINARIES_DIR)/bl32.elf
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
UBOOT_MULTIBOARD_MAKE_OPTS += BL31=$(BINARIES_DIR)/bl31.elf
UBOOT_MULTIBOARD_FRAGMENTS += $(UBOOT_MULTIBOARD_PKGDIR)/rk3399.config.fragment
else ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_H5)$(BR2_PACKAGE_BATOCERA_TARGET_H6)$(BR2_PACKAGE_BATOCERA_TARGET_H616),)
UBOOT_MULTIBOARD_MAKE_OPTS += BL31=$(BINARIES_DIR)/bl31.bin SCP=/dev/null
endif

# Host tools link against buildroot's host libraries, not the target sysroot
UBOOT_MULTIBOARD_BUILD_ENV = \
	$(TARGET_MAKE_ENV) \
	PKG_CONFIG="$(PKG_CONFIG_HOST_BINARY)" \
	PKG_CONFIG_SYSROOT_DIR="/" \
	PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1 \
	PKG_CONFIG_ALLOW_SYSTEM_LIBS=1 \
	PKG_CONFIG_LIBDIR="$(HOST_DIR)/lib/pkgconfig:$(HOST_DIR)/share/pkgconfig"

# One patched source tree, one out-of-tree build per board
define UBOOT_MULTIBOARD_CONFIGURE_BOARD
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) O=$(@D)/build-$(1) \
		$(UBOOT_MULTIBOARD_MAKE_OPTS) $(1)_defconfig
	support/kconfig/merge_config.sh -m -O $(@D)/build-$(1) \
		$(@D)/build-$(1)/.config $(UBOOT_MULTIBOARD_FRAGMENTS)
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) O=$(@D)/build-$(1) \
		$(UBOOT_MULTIBOARD_MAKE_OPTS) olddefconfig
endef

define UBOOT_MULTIBOARD_CONFIGURE_CMDS
	$(foreach board,$(UBOOT_MULTIBOARD_CONFIGS),\
		$(call UBOOT_MULTIBOARD_CONFIGURE_BOARD,$(board))$(sep))
endef

define UBOOT_MULTIBOARD_BUILD_CMDS
	$(foreach board,$(UBOOT_MULTIBOARD_CONFIGS),\
		$(UBOOT_MULTIBOARD_BUILD_ENV) $(MAKE) -C $(@D) O=$(@D)/build-$(board) \
			$(UBOOT_MULTIBOARD_MAKE_OPTS) all$(sep))
endef

define UBOOT_MULTIBOARD_INSTALL_IMAGES_CMDS
	$(foreach board,$(UBOOT_MULTIBOARD_CONFIGS),\
		mkdir -p $(BINARIES_DIR)/uboot-multiboard/$(board)$(sep)\
		$(foreach bin,$(UBOOT_MULTIBOARD_BINARIES),\
			cp -f $(@D)/build-$(board)/$(bin) \
				$(BINARIES_DIR)/uboot-multiboard/$(board)/$(sep)))
endef

$(eval $(generic-package))
