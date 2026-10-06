################################################################################
#
# uboot-rk3326
#
################################################################################

UBOOT_RK3326_VERSION = 2492a3e467e332e2350d987234ce6123700b3392
UBOOT_RK3326_SITE = $(call github,ROCKNIX,hardkernel-uboot,$(UBOOT_RK3326_VERSION))
UBOOT_RK3326_LICENSE = GPL-2.0+
UBOOT_RK3326_LICENSE_FILES = Licenses/README
UBOOT_RK3326_INSTALL_IMAGES = YES

# Rockchip DDR init, miniloader, BL31 and the loaderimage/trust_merger tools
UBOOT_RK3326_RKBIN_COMMIT = 74213af1e952c4683d2e35952507133b61394862
UBOOT_RK3326_EXTRA_DOWNLOADS = \
    https://github.com/rockchip-linux/rkbin/archive/$(UBOOT_RK3326_RKBIN_COMMIT)/rkbin-$(UBOOT_RK3326_RKBIN_COMMIT).tar.gz

UBOOT_RK3326_DEPENDENCIES = host-pkgconf host-bison host-flex host-dtc host-openssl

define UBOOT_RK3326_EXTRACT_RKBIN
    mkdir -p $(@D)/rkbin
    $(TAR) -xf $(UBOOT_RK3326_DL_DIR)/rkbin-$(UBOOT_RK3326_RKBIN_COMMIT).tar.gz \
        -C $(@D)/rkbin --strip-components=1
    cp $(UBOOT_RK3326_PKGDIR)/rocknix_rk3326_defconfig $(@D)/configs/
endef
UBOOT_RK3326_POST_EXTRACT_HOOKS += UBOOT_RK3326_EXTRACT_RKBIN

UBOOT_RK3326_RKBIN = $(@D)/rkbin
UBOOT_RK3326_DDR_BIN = $(UBOOT_RK3326_RKBIN)/bin/rk33/rk3326_ddr_333MHz_v2.11.bin
UBOOT_RK3326_MINILOADER = $(UBOOT_RK3326_RKBIN)/bin/rk33/rk3326_miniloader_v1.40.bin
UBOOT_RK3326_BL31 = $(UBOOT_RK3326_RKBIN)/bin/rk33/rk3326_bl31_v1.34.elf

UBOOT_RK3326_MAKE_OPTS = \
    ARCH=arm \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCC="$(HOSTCC)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)" \
    CONFIG_MKIMAGE_DTC_PATH="scripts/dtc/dtc"

define UBOOT_RK3326_CONFIGURE_CMDS
    $(TARGET_MAKE_ENV) $(MAKE1) -C $(@D) $(UBOOT_RK3326_MAKE_OPTS) rocknix_rk3326_defconfig
endef

define UBOOT_RK3326_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE1) -C $(@D) $(UBOOT_RK3326_MAKE_OPTS)
    $(@D)/tools/mkimage -n px30 -T rksd -d $(UBOOT_RK3326_DDR_BIN) $(@D)/idbloader.img
    cat $(UBOOT_RK3326_MINILOADER) >> $(@D)/idbloader.img
    $(UBOOT_RK3326_RKBIN)/tools/loaderimage --pack --uboot $(@D)/u-boot-dtb.bin \
        $(@D)/uboot.img 0x00200000
    printf '[BL30_OPTION]\nSEC=0\n[BL31_OPTION]\nSEC=1\nPATH=%s\nADDR=0x00010000\n[BL32_OPTION]\nSEC=0\n[BL33_OPTION]\nSEC=0\n[OUTPUT]\nPATH=%s\n' \
        $(UBOOT_RK3326_BL31) $(@D)/trust.img > $(@D)/trust.ini
    $(UBOOT_RK3326_RKBIN)/tools/trust_merger $(@D)/trust.ini
endef

define UBOOT_RK3326_INSTALL_IMAGES_CMDS
    $(INSTALL) -D -m 0644 $(@D)/idbloader.img $(BINARIES_DIR)/idbloader.img
    $(INSTALL) -D -m 0644 $(@D)/uboot.img $(BINARIES_DIR)/uboot.img
    $(INSTALL) -D -m 0644 $(@D)/trust.img $(BINARIES_DIR)/trust.img
endef

$(eval $(generic-package))
