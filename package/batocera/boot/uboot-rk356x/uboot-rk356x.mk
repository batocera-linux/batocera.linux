################################################################################
#
# uboot-rk356x
#
################################################################################

UBOOT_RK356X_VERSION = 2026.07
UBOOT_RK356X_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_RK356X_SOURCE = u-boot-$(UBOOT_RK356X_VERSION).tar.bz2
UBOOT_RK356X_LICENSE = GPL-2.0+
UBOOT_RK356X_LICENSE_FILES = Licenses/README
UBOOT_RK356X_INSTALL_IMAGES = YES

# Rockchip binary blobs for DDR init and ATF (BL31)
UBOOT_RK356X_RKBIN_COMMIT = ecb4fcbe954edf38b3ae037d5de6d9f5bccf81f4
UBOOT_RK356X_EXTRA_DOWNLOADS = \
    https://github.com/rockchip-linux/rkbin/archive/$(UBOOT_RK356X_RKBIN_COMMIT)/rkbin-$(UBOOT_RK356X_RKBIN_COMMIT).tar.gz

UBOOT_RK356X_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex \
    host-python-setuptools host-dtc host-swig host-gnutls host-python-pyelftools

# Extract the full rkbin repository
define UBOOT_RK356X_EXTRACT_RKBIN
    mkdir -p $(@D)/rkbin
    $(TAR) -xf $(UBOOT_RK356X_DL_DIR)/rkbin-$(UBOOT_RK356X_RKBIN_COMMIT).tar.gz \
        -C $(@D)/rkbin --strip-components=1
endef
UBOOT_RK356X_POST_EXTRACT_HOOKS += UBOOT_RK356X_EXTRACT_RKBIN

# RK356x Specific BL31 Path
UBOOT_RK356X_BL31 = $(@D)/rkbin/bin/rk35/rk3568_bl31_v1.46.elf

UBOOT_RK356X_MAKE_OPTS = \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCC="$(HOSTCC)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)" \
    BL31=$(UBOOT_RK356X_BL31)

# Board/Defconfig/TPL triplets
# (Output directory name / U-Boot defconfig / Rockchip DDR binary file)
UBOOT_RK356X_BUILDPAIR += uboot-rk356x/quartz64-a-rk3566_defconfig/rk3568_ddr_1056MHz_v1.25.bin
UBOOT_RK356X_BUILDPAIR += rock-3a/rock-3a-rk3568_defconfig/rk3568_ddr_1560MHz_v1.25.bin
UBOOT_RK356X_BUILDPAIR += rock-3c/rock-3c-rk3566_defconfig/rk3568_ddr_1056MHz_v1.25.bin
UBOOT_RK356X_BUILDPAIR += orangepi-3b/orangepi-3b-rk3566_defconfig/rk3568_ddr_1056MHz_v1.25.bin
UBOOT_RK356X_BUILDPAIR += powkiddy-x55/powkiddy-x55-rk3566_defconfig/rk3568_ddr_1056MHz_v1.25.bin
UBOOT_RK356X_BUILDPAIR += radxa-zero-3/radxa-zero-3-rk3566_defconfig/rk3568_ddr_1056MHz_v1.25.bin
UBOOT_RK356X_BUILDPAIR += anbernic-rgxx3/anbernic-rgxx3-rk3566_defconfig/rk3568_ddr_1056MHz_v1.25.bin
UBOOT_RK356X_BUILDPAIR += uboot-odroid-m1s/odroid-m1s-rk3566_defconfig/rk3568_ddr_1056MHz_v1.25.bin
UBOOT_RK356X_BUILDPAIR += uboot-odroid-m1/odroid-m1-rk3568_defconfig/rk3568_ddr_1560MHz_v1.25.bin

define UBOOT_RK356X_BUILD_BOOTLOADER
    $(eval board_defconfig_tpl = $(subst /, ,$(pair)))
    $(eval board = $(word 1, $(board_defconfig_tpl)))
    $(eval defconfig = $(word 2, $(board_defconfig_tpl)))
    $(eval tpl = $(word 3, $(board_defconfig_tpl)))
    @echo
    @echo "---- Building Mainline U-Boot for $(board) ----"
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK356X_MAKE_OPTS) \
        ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/$(tpl) mrproper
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK356X_MAKE_OPTS) \
        ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/$(tpl) $(defconfig)
    $(@D)/scripts/config --file $(@D)/.config --disable CONFIG_TOOLS_MKEFICAPSULE
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK356X_MAKE_OPTS) \
        ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/$(tpl) olddefconfig
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK356X_MAKE_OPTS) \
        ROCKCHIP_TPL=$(@D)/rkbin/bin/rk35/$(tpl)
    mkdir -p $(@D)/staging/$(board)
    cp -v $(@D)/u-boot-rockchip.bin $(@D)/staging/$(board)/
    # Binman generates the SPI binary if CONFIG_ROCKCHIP_SPI_IMAGE is enabled
    if [ -f $(@D)/u-boot-rockchip-spi.bin ]; then \
        cp -v $(@D)/u-boot-rockchip-spi.bin $(@D)/staging/$(board)/; \
    fi
endef

define UBOOT_RK356X_BUILD_CMDS
    mkdir -p $(@D)/staging
    $(foreach pair, $(UBOOT_RK356X_BUILDPAIR), $(UBOOT_RK356X_BUILD_BOOTLOADER))
endef

define UBOOT_RK356X_INSTALL_IMAGES_CMDS
	$(foreach pair, $(UBOOT_RK356X_BUILDPAIR), \
		board=$$(echo $(pair) | cut -d'/' -f1); \
		mkdir -p $(BINARIES_DIR)/$$board; \
		cp -v $(@D)/staging/$$board/u-boot-rockchip.bin $(BINARIES_DIR)/$$board/; \
		if [ -f $(@D)/staging/$$board/u-boot-rockchip-spi.bin ]; then \
			cp -v $(@D)/staging/$$board/u-boot-rockchip-spi.bin $(BINARIES_DIR)/$$board/; \
		fi; \
	)
endef

$(eval $(generic-package))
