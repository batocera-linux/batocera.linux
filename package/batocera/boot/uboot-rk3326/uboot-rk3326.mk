################################################################################
#
# uboot-rk3326
#
################################################################################

UBOOT_RK3326_VERSION = 611716febddb824a7203d0d3b5d399608a54ccf6
UBOOT_RK3326_SITE = https://github.com/ROCKNIX/hardkernel-uboot
UBOOT_RK3326_SITE_METHOD = git
UBOOT_RK3326_LICENSE = GPL-2.0+
UBOOT_RK3326_LICENSE_FILES = Licenses/README
UBOOT_RK3326_INSTALL_IMAGES = YES

UBOOT_RK3326_DEPENDENCIES = host-pkgconf host-bison host-flex \
    host-python-setuptools host-dtc host-swig host-uboot-tools \
    host-gnutls host-openssl host-zlib

UBOOT_RK3326_RKBIN_DIR = $(@D)/tools/rk_tools

UBOOT_RK3326_DDR_BIN = $(UBOOT_RK3326_RKBIN_DIR)/bin/rk33/rk3326_ddr_333MHz_v1.10.bin
UBOOT_RK3326_MINILOADER = $(UBOOT_RK3326_RKBIN_DIR)/bin/rk33/rk3326_miniloader_v1.12.bin

UBOOT_RK3326_LOADERIMAGE = $(@D)/tools/loaderimage
UBOOT_RK3326_TRUSTMERGER = $(@D)/tools/trust_merger

UBOOT_RK3326_MAKE_OPTS = \
    CROSS_COMPILE="$(TARGET_CROSS)" \
    HOSTCFLAGS="$(HOST_CFLAGS)" \
    HOSTLDFLAGS="$(HOST_LDFLAGS)"

define UBOOT_RK3326_CONFIGURE_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3326_MAKE_OPTS) \
        odroidgoa_defconfig
endef

define UBOOT_RK3326_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(UBOOT_RK3326_MAKE_OPTS) all
endef

define UBOOT_RK3326_INSTALL_IMAGES_CMDS
    # 1. Build idbloader.img
    $(HOST_DIR)/bin/mkimage -n px30 -T rksd -d $(UBOOT_RK3326_DDR_BIN) $(@D)/idbloader.img
    cat $(UBOOT_RK3326_MINILOADER) >> $(@D)/idbloader.img
    $(INSTALL) -D -m 0644 $(@D)/idbloader.img $(BINARIES_DIR)/idbloader.img

    # 2. Build uboot.img
    $(UBOOT_RK3326_LOADERIMAGE) --pack --uboot $(@D)/u-boot.bin \
        $(@D)/uboot.img 0x00200000
    $(INSTALL) -D -m 0644 $(@D)/uboot.img $(BINARIES_DIR)/uboot.img

    # 3. Build trust.img
    chmod +x $(UBOOT_RK3326_TRUSTMERGER)
    cd $(UBOOT_RK3326_RKBIN_DIR) && \
        ../../tools/trust_merger \
        --rsa 3 \
        --replace tools/rk_tools/ ./ \
        ./RKTRUST/RK3326TRUST.ini
    
    $(INSTALL) -D -m 0644 $(UBOOT_RK3326_RKBIN_DIR)/trust.img $(BINARIES_DIR)/trust.img
endef

$(eval $(generic-package))
