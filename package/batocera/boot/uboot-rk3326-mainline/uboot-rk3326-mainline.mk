################################################################################
#
# uboot-rk3326-mainline
#
################################################################################

UBOOT_RK3326_MAINLINE_VERSION = 2026.07
UBOOT_RK3326_MAINLINE_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_RK3326_MAINLINE_SOURCE = u-boot-$(UBOOT_RK3326_MAINLINE_VERSION).tar.bz2
UBOOT_RK3326_MAINLINE_LICENSE = GPL-2.0+
UBOOT_RK3326_MAINLINE_LICENSE_FILES = Licenses/README
UBOOT_RK3326_MAINLINE_INSTALL_IMAGES = YES

# Rockchip DDR init, miniloader, BL31 and the loaderimage/trust_merger tools
UBOOT_RK3326_MAINLINE_RKBIN_COMMIT = 74213af1e952c4683d2e35952507133b61394862
UBOOT_RK3326_MAINLINE_EXTRA_DOWNLOADS = \
    https://github.com/rockchip-linux/rkbin/archive/$(UBOOT_RK3326_MAINLINE_RKBIN_COMMIT)/rkbin-$(UBOOT_RK3326_MAINLINE_RKBIN_COMMIT).tar.gz

UBOOT_RK3326_MAINLINE_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex

define UBOOT_RK3326_MAINLINE_EXTRACT_RKBIN
    mkdir -p $(@D)/rkbin
    $(TAR) -xf $(UBOOT_RK3326_MAINLINE_DL_DIR)/rkbin-$(UBOOT_RK3326_MAINLINE_RKBIN_COMMIT).tar.gz \
        -C $(@D)/rkbin --strip-components=1
endef
UBOOT_RK3326_MAINLINE_POST_EXTRACT_HOOKS += UBOOT_RK3326_MAINLINE_EXTRACT_RKBIN

UBOOT_RK3326_MAINLINE_RKBIN = $(@D)/rkbin
UBOOT_RK3326_MAINLINE_DDR_BIN = $(UBOOT_RK3326_MAINLINE_RKBIN)/bin/rk33/rk3326_ddr_333MHz_v2.11.bin
UBOOT_RK3326_MAINLINE_MINILOADER = $(UBOOT_RK3326_MAINLINE_RKBIN)/bin/rk33/rk3326_miniloader_v1.40.bin
UBOOT_RK3326_MAINLINE_BL31 = $(UBOOT_RK3326_MAINLINE_RKBIN)/bin/rk33/rk3326_bl31_v1.34.elf

UBOOT_RK3326_MAINLINE_MAKE_OPTS = \
    ARCH=arm \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCC="$(HOSTCC)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)" \
    NO_PYTHON=1

ifeq ($(BR2_PACKAGE_UBOOT_RK3326_MAINLINE_UART5),y)
UBOOT_RK3326_MAINLINE_DEPENDENCIES += host-python3
define UBOOT_RK3326_MAINLINE_UART5_CONFIG
    $(@D)/scripts/config --file $(@D)/.config \
        --set-val CONFIG_DEBUG_UART_BASE 0xFF178000 \
        --set-str CONFIG_DEVICE_TREE_INCLUDES "rk3326-odroid-go2-emmc.dtsi rk3326-odroid-go2-uart5.dtsi"
endef
define UBOOT_RK3326_MAINLINE_UART5_DDR_BIN
    cp $(UBOOT_RK3326_MAINLINE_DDR_BIN) $(@D)/ddr.bin
    $(HOST_DIR)/bin/python3 $(UBOOT_RK3326_MAINLINE_RKBIN)/tools/ddrbin_tool.py rk3326 -g $(@D)/ddr.txt $(@D)/ddr.bin
    sed -i 's|uart id=.*$$|uart id=5|' $(@D)/ddr.txt
    $(HOST_DIR)/bin/python3 $(UBOOT_RK3326_MAINLINE_RKBIN)/tools/ddrbin_tool.py rk3326 $(@D)/ddr.txt $(@D)/ddr.bin
endef
UBOOT_RK3326_MAINLINE_IDB_DDR_BIN = $(@D)/ddr.bin
else
UBOOT_RK3326_MAINLINE_IDB_DDR_BIN = $(UBOOT_RK3326_MAINLINE_DDR_BIN)
endif

define UBOOT_RK3326_MAINLINE_CONFIGURE_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3326_MAINLINE_MAKE_OPTS) \
        rk3326-handheld_defconfig
    $(UBOOT_RK3326_MAINLINE_UART5_CONFIG)
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3326_MAINLINE_MAKE_OPTS) olddefconfig
endef

define UBOOT_RK3326_MAINLINE_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3326_MAINLINE_MAKE_OPTS) u-boot-dtb.bin
    $(UBOOT_RK3326_MAINLINE_UART5_DDR_BIN)
    # the RK3326 bootrom loads the legacy idbloader/uboot.img/trust.img layout
    $(@D)/tools/mkimage -n px30 -T rksd -d $(UBOOT_RK3326_MAINLINE_IDB_DDR_BIN) $(@D)/idbloader.img
    cat $(UBOOT_RK3326_MAINLINE_MINILOADER) >> $(@D)/idbloader.img
    $(UBOOT_RK3326_MAINLINE_RKBIN)/tools/loaderimage --pack --uboot $(@D)/u-boot-dtb.bin \
        $(@D)/uboot.img 0x00200000
    printf '[BL30_OPTION]\nSEC=0\n[BL31_OPTION]\nSEC=1\nPATH=%s\nADDR=0x00010000\n[BL32_OPTION]\nSEC=0\n[BL33_OPTION]\nSEC=0\n[OUTPUT]\nPATH=%s\n' \
        $(UBOOT_RK3326_MAINLINE_BL31) $(@D)/trust.img > $(@D)/trust.ini
    $(UBOOT_RK3326_MAINLINE_RKBIN)/tools/trust_merger $(@D)/trust.ini
endef

define UBOOT_RK3326_MAINLINE_INSTALL_IMAGES_CMDS
    $(INSTALL) -D -m 0644 $(@D)/idbloader.img $(BINARIES_DIR)/uboot-rk3326-mainline/idbloader.img
    $(INSTALL) -D -m 0644 $(@D)/uboot.img $(BINARIES_DIR)/uboot-rk3326-mainline/uboot.img
    $(INSTALL) -D -m 0644 $(@D)/trust.img $(BINARIES_DIR)/uboot-rk3326-mainline/trust.img
endef

$(eval $(generic-package))
