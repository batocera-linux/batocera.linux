################################################################################
#
# uboot-rk3588
#
################################################################################

UBOOT_RK3588_VERSION = 2025.10
UBOOT_RK3588_SITE = https://ftp.denx.de/pub/u-boot
UBOOT_RK3588_SOURCE = u-boot-$(UBOOT_RK3588_VERSION).tar.bz2
UBOOT_RK3588_LICENSE = GPL-2.0+
UBOOT_RK3588_LICENSE_FILES = Licenses/README
UBOOT_RK3588_INSTALL_IMAGES = YES

# Latest RKBin blobs for RK3588
UBOOT_RK3588_RKBIN_COMMIT = 74213af1e952c4683d2e35952507133b61394862
UBOOT_RK3588_EXTRA_DOWNLOADS = \
    https://github.com/rockchip-linux/rkbin/archive/$(UBOOT_RK3588_RKBIN_COMMIT)/rkbin-$(UBOOT_RK3588_RKBIN_COMMIT).tar.gz

# Modern U-Boot dependencies
UBOOT_RK3588_DEPENDENCIES = host-pkgconf host-openssl host-bison host-flex \
    host-python-setuptools host-dtc host-swig host-gnutls host-python-pyelftools

# Extract the full rkbin repository
define UBOOT_RK3588_EXTRACT_RKBIN
    mkdir -p $(@D)/rkbin
    $(TAR) -xf $(UBOOT_RK3588_DL_DIR)/rkbin-$(UBOOT_RK3588_RKBIN_COMMIT).tar.gz \
        -C $(@D)/rkbin --strip-components=1
endef
UBOOT_RK3588_POST_EXTRACT_HOOKS += UBOOT_RK3588_EXTRACT_RKBIN

# RK3588 Specific Blob Paths
UBOOT_RK3588_BL31 = $(@D)/rkbin/bin/rk35/rk3588_bl31_v1.51.elf
UBOOT_RK3588_TPL  = $(@D)/rkbin/bin/rk35/rk3588_ddr_lp4_2112MHz_lp5_2400MHz_v1.19.bin

UBOOT_RK3588_MAKE_OPTS = \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)" \
    BL31=$(UBOOT_RK3588_BL31) \
    ROCKCHIP_TPL=$(UBOOT_RK3588_TPL)

# Board/Defconfig pairs (Updated for Mainline naming conventions)
UBOOT_RK3588_BUILDPAIR += orangepi-5/orangepi-5-rk3588s_defconfig
UBOOT_RK3588_BUILDPAIR += rock-5a/rock5a-rk3588s_defconfig
UBOOT_RK3588_BUILDPAIR += rock-5b/rock5b-rk3588_defconfig
UBOOT_RK3588_BUILDPAIR += nanopi-r6/nanopi-r6s-rk3588s_defconfig
UBOOT_RK3588_BUILDPAIR += cm3588-nas/cm3588-nas-rk3588_defconfig
UBOOT_RK3588_BUILDPAIR += rock-5c/rock-5c-rk3588s_defconfig
UBOOT_RK3588_BUILDPAIR += orangepi-5-plus/orangepi-5-plus-rk3588_defconfig
UBOOT_RK3588_BUILDPAIR += khadas-edge2/khadas-edge2-rk3588s_defconfig
UBOOT_RK3588_BUILDPAIR += coolpi-4b/coolpi-4b-rk3588s_defconfig
UBOOT_RK3588_BUILDPAIR += gameforce-ace/gameforce-ace-rk3588s_defconfig
UBOOT_RK3588_BUILDPAIR += quartzpro64/quartzpro64-rk3588_defconfig
UBOOT_RK3588_BUILDPAIR += indiedroid-nova/nova-rk3588s_defconfig

define UBOOT_RK3588_BUILD_BOOTLOADER
    $(eval board_defconfig = $(subst /, ,$(pair)))
    $(eval board = $(word 1, $(board_defconfig)))
    $(eval defconfig = $(word 2, $(board_defconfig)))
    @echo
    @echo "---- Building Mainline U-Boot for $(board) ----"
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3588_MAKE_OPTS) mrproper
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3588_MAKE_OPTS) $(defconfig)
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3588_MAKE_OPTS)
    mkdir -p $(@D)/staging/$(board)
    cp -v $(@D)/u-boot-rockchip.bin $(@D)/staging/$(board)/
endef

define UBOOT_RK3588_BUILD_CMDS
    mkdir -p $(@D)/staging
    $(foreach pair, $(UBOOT_RK3588_BUILDPAIR), $(UBOOT_RK3588_BUILD_BOOTLOADER))
endef

define UBOOT_RK3588_INSTALL_IMAGES_CMDS
    $(foreach pair, $(UBOOT_RK3588_BUILDPAIR), \
        $(eval board = $(word 1, $(subst /, ,$(pair)))) \
        mkdir -p $(BINARIES_DIR)/$(board); \
        cp -v $(@D)/staging/$(board)/u-boot-rockchip.bin $(BINARIES_DIR)/$(board)/u-boot-rockchip.bin; \
    )
endef

$(eval $(generic-package))
