################################################################################
#
# uboot for rk3288 tinkerboard
#
################################################################################
UBOOT_TINKERBOARD_VERSION = $(call qstrip,$(BR2_PACKAGE_UBOOT_TINKERBOARD_VERSION))
UBOOT_TINKERBOARD_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_TINKERBOARD_DL_SUBDIR = uboot
UBOOT_TINKERBOARD_SOURCE = u-boot-$(UBOOT_TINKERBOARD_VERSION).tar.bz2
UBOOT_TINKERBOARD_DEPENDENCIES = arm-trusted-firmware
UBOOT_TINKERBOARD_DEPENDENCIES += host-python3 host-python-setuptools
UBOOT_TINKERBOARD_DEPENDENCIES += host-swig
UBOOT_TINKERBOARD_DEPENDENCIES += host-openssl

UBOOT_TINKERBOARD_KCONFIG_DEFCONFIG = tinker-s-rk3288_defconfig
UBOOT_TINKERBOARD_KCONFIG_FRAGMENT_FILES = $(UBOOT_TINKERBOARD_PKGDIR)/../../uboot.config.fragment $(UBOOT_TINKERBOARD_PKGDIR)/../uboot.config.fragment $(UBOOT_TINKERBOARD_PKGDIR)/uboot.config.fragment

# Apply common and soc specific patches before board specific ones
define UBOOT_TINKERBOARD_APPLY_LOCAL_PATCHES
	if ls $(UBOOT_TINKERBOARD_PKGDIR)/../../*.patch > /dev/null 2>&1; then \
		$(APPLY_PATCHES) $(@D) $(UBOOT_TINKERBOARD_PKGDIR)/../.. *.patch; \
	fi
	if ls $(UBOOT_TINKERBOARD_PKGDIR)/../*.patch > /dev/null 2>&1; then \
		$(APPLY_PATCHES) $(@D) $(UBOOT_TINKERBOARD_PKGDIR)/.. *.patch; \
	fi
endef
UBOOT_TINKERBOARD_PRE_PATCH_HOOKS += UBOOT_TINKERBOARD_APPLY_LOCAL_PATCHES

# *_OPTS and * _BUILD_CMDS are adaptation of ones in uboot.mk. Added "-I $(HOST_DIR)/include"
# because otherwise build seemed to be mixing openssl headers from build host/docker
# (openssl 3.0.2) and buildroot host-openssl (1.1.1q).
UBOOT_TINKERBOARD_MAKE_OPTS += \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	HOSTCC="$(HOSTCC) -I $(HOST_DIR)/include $(subst -I/,-isystem /,$(subst -I /,-isystem /,$(HOST_CFLAGS)))" \
	HOSTLDFLAGS="$(HOST_LDFLAGS)" \
	BL32="$(BINARIES_DIR)/bl32.elf"

UBOOT_TINKERBOARD_KCONFIG_OPTS = $(UBOOT_TINKERBOARD_MAKE_OPTS) HOSTCC="$(HOSTCC_NOCCACHE)" HOSTLDFLAGS=""

define UBOOT_TINKERBOARD_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) \
		PKG_CONFIG="$(PKG_CONFIG_HOST_BINARY)" \
		PKG_CONFIG_SYSROOT_DIR="/" \
		PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1 \
		PKG_CONFIG_ALLOW_SYSTEM_LIBS=1 \
		PKG_CONFIG_LIBDIR="$(HOST_DIR)/lib/pkgconfig:$(HOST_DIR)/share/pkgconfig" \
		$(MAKE) -C "$(@D)" $(UBOOT_TINKERBOARD_MAKE_OPTS) all
endef

define UBOOT_TINKERBOARD_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot/rk3288/tinkerboard
	cp -f $(@D)/{idbloader.img,u-boot.img} $(BINARIES_DIR)/uboot/rk3288/tinkerboard
endef

$(eval $(kconfig-package))
