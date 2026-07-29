################################################################################
#
# uboot-rk3576
#
################################################################################

UBOOT_RK3576_VERSION = 2026.07
UBOOT_RK3576_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_RK3576_SOURCE = u-boot-$(UBOOT_RK3576_VERSION).tar.bz2
UBOOT_RK3576_LICENSE = GPL-2.0+
UBOOT_RK3576_LICENSE_FILES = Licenses/README
UBOOT_RK3576_INSTALL_IMAGES = YES

# Rockchip binary blobs for DDR init and ATF (BL31)
UBOOT_RK3576_RKBIN_COMMIT = ecb4fcbe954edf38b3ae037d5de6d9f5bccf81f4
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
    BL31=$(@D)/rkbin/bin/rk35/rk3576_bl31_v1.24.elf \
    ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/rk3576_ddr_lp4_2112MHz_lp5_2736MHz_v1.12.bin

define UBOOT_RK3576_CONFIGURE_CMDS
    # Using generic-rk3576_defconfig as the baseline configuration
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3576_MAKE_OPTS) \
        generic-rk3576_defconfig
    # Disable CONFIG_TOOLS_MKEFICAPSULE to bypass GnuTLS linker issues
    $(@D)/scripts/config --file $(@D)/.config --disable CONFIG_TOOLS_MKEFICAPSULE
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3576_MAKE_OPTS) olddefconfig
endef

define UBOOT_RK3576_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3576_MAKE_OPTS)
endef

define UBOOT_RK3576_INSTALL_IMAGES_CMDS
    mkdir -p $(BINARIES_DIR)/uboot-rk3576
    # u-boot-rockchip.bin contains both the idbloader.img and u-boot.itb
    $(INSTALL) -D -m 0644 $(@D)/u-boot-rockchip.bin \
        $(BINARIES_DIR)/uboot-rk3576/u-boot-rockchip.bin
endef

$(eval $(generic-package))
