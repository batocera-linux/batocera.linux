################################################################################
#
# uboot-rk3562
#
################################################################################

UBOOT_RK3562_VERSION = 2026.07
UBOOT_RK3562_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_RK3562_SOURCE = u-boot-$(UBOOT_RK3562_VERSION).tar.bz2
UBOOT_RK3562_LICENSE = GPL-2.0+
UBOOT_RK3562_LICENSE_FILES = Licenses/README
UBOOT_RK3562_INSTALL_IMAGES = YES

UBOOT_RK3562_DEPENDENCIES = rkbin host-pkgconf host-openssl host-bison \
    host-flex host-python-setuptools host-dtc host-swig host-gnutls \
    host-python-pyelftools

UBOOT_RK3562_MAKE_OPTS = \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCC="$(HOSTCC)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)"

# board:defconfig:bl31:tpl
UBOOT_RK3562_BUILD_TARGETS = \
    kickpi-k3b:kickpi-k3b-rk3562_defconfig:$(BINARIES_DIR)/rkbin/bin/rk35/rk3562_bl31_v1.23.elf:$(BINARIES_DIR)/rkbin/bin/rk35/rk3562_ddr_1056MHz_v1.09.bin

define UBOOT_RK3562_BUILD_BOOTLOADER
    $(eval target_parts = $(subst :, ,$(target)))
    $(eval board = $(word 1, $(target_parts)))
    $(eval defconfig = $(word 2, $(target_parts)))
    $(eval bl31 = $(word 3, $(target_parts)))
    $(eval tpl = $(word 4, $(target_parts)))
    @echo
    @echo "---- Building mainline U-Boot for $(board) ----"
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3562_MAKE_OPTS) mrproper
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3562_MAKE_OPTS) $(defconfig)
    sed -i 's/^CONFIG_BOOTDELAY=.*/CONFIG_BOOTDELAY=1/' $(@D)/.config
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3562_MAKE_OPTS) BL31="$(bl31)" ROCKCHIP_TPL="$(tpl)"
    mkdir -p $(@D)/staging/$(board)
    cp -v $(@D)/idbloader.img $(@D)/staging/$(board)/
    cp -v $(@D)/u-boot.itb $(@D)/staging/$(board)/
endef

define UBOOT_RK3562_BUILD_CMDS
    mkdir -p $(@D)/staging
    $(foreach target, $(UBOOT_RK3562_BUILD_TARGETS), $(UBOOT_RK3562_BUILD_BOOTLOADER))
endef

define UBOOT_RK3562_INSTALL_IMAGES_CMDS
    $(foreach target, $(UBOOT_RK3562_BUILD_TARGETS), \
        $(eval board = $(word 1, $(subst :, ,$(target)))) \
        mkdir -p $(BINARIES_DIR)/uboot-rk3562/$(board); \
        cp -v $(@D)/staging/$(board)/idbloader.img $(BINARIES_DIR)/uboot-rk3562/$(board)/idbloader.img; \
        cp -v $(@D)/staging/$(board)/u-boot.itb $(BINARIES_DIR)/uboot-rk3562/$(board)/u-boot.itb; \
    )
endef

$(eval $(generic-package))
