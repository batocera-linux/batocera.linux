################################################################################
#
# uboot for rk3399 rockpro64
#
################################################################################
UBOOT_ROCKPRO64_VERSION = $(call qstrip,$(BR2_PACKAGE_UBOOT_ROCKPRO64_VERSION))
UBOOT_ROCKPRO64_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_ROCKPRO64_DL_SUBDIR = uboot
UBOOT_ROCKPRO64_SOURCE = u-boot-$(UBOOT_ROCKPRO64_VERSION).tar.bz2
UBOOT_ROCKPRO64_DEPENDENCIES = arm-trusted-firmware
UBOOT_ROCKPRO64_DEPENDENCIES += host-python3 host-python-setuptools
UBOOT_ROCKPRO64_DEPENDENCIES += host-swig
UBOOT_ROCKPRO64_DEPENDENCIES += host-openssl

UBOOT_ROCKPRO64_KCONFIG_DEFCONFIG = rockpro64-rk3399_defconfig
UBOOT_ROCKPRO64_KCONFIG_FRAGMENT_FILES = $(UBOOT_ROCKPRO64_PKGDIR)/../../uboot.config.fragment $(UBOOT_ROCKPRO64_PKGDIR)/../uboot.config.fragment $(UBOOT_ROCKPRO64_PKGDIR)/uboot.config.fragment

# Apply common and soc specific patches before board specific ones
define UBOOT_ROCKPRO64_APPLY_LOCAL_PATCHES
	if ls $(UBOOT_ROCKPRO64_PKGDIR)/../../*.patch > /dev/null 2>&1; then \
		$(APPLY_PATCHES) $(@D) $(UBOOT_ROCKPRO64_PKGDIR)/../.. *.patch; \
	fi
	if ls $(UBOOT_ROCKPRO64_PKGDIR)/../*.patch > /dev/null 2>&1; then \
		$(APPLY_PATCHES) $(@D) $(UBOOT_ROCKPRO64_PKGDIR)/.. *.patch; \
	fi
endef
UBOOT_ROCKPRO64_PRE_PATCH_HOOKS += UBOOT_ROCKPRO64_APPLY_LOCAL_PATCHES

# *_OPTS and * _BUILD_CMDS are adaptation of ones in uboot.mk. Added "-I $(HOST_DIR)/include"
# because otherwise build seemed to be mixing openssl headers from build host/docker
# (openssl 3.0.2) and buildroot host-openssl (1.1.1q).
UBOOT_ROCKPRO64_MAKE_OPTS += \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	HOSTCC="$(HOSTCC) -I $(HOST_DIR)/include $(subst -I/,-isystem /,$(subst -I /,-isystem /,$(HOST_CFLAGS)))" \
	HOSTLDFLAGS="$(HOST_LDFLAGS)" \
	BL31="$(BINARIES_DIR)/bl31.elf"

UBOOT_ROCKPRO64_KCONFIG_OPTS = $(UBOOT_ROCKPRO64_MAKE_OPTS) HOSTCC="$(HOSTCC_NOCCACHE)" HOSTLDFLAGS=""

define UBOOT_ROCKPRO64_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) \
		PKG_CONFIG="$(PKG_CONFIG_HOST_BINARY)" \
		PKG_CONFIG_SYSROOT_DIR="/" \
		PKG_CONFIG_ALLOW_SYSTEM_CFLAGS=1 \
		PKG_CONFIG_ALLOW_SYSTEM_LIBS=1 \
		PKG_CONFIG_LIBDIR="$(HOST_DIR)/lib/pkgconfig:$(HOST_DIR)/share/pkgconfig" \
		$(MAKE) -C "$(@D)" $(UBOOT_ROCKPRO64_MAKE_OPTS) all
endef

define UBOOT_ROCKPRO64_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/uboot/rk3399/rockpro64
	cp -f $(@D)/{idbloader.img,u-boot.itb} $(BINARIES_DIR)/uboot/rk3399/rockpro64
endef

$(eval $(kconfig-package))
