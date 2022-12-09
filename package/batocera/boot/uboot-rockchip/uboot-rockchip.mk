################################################################################
#
# Prebuilt mainline U-Boot for Rockchip boards
#
################################################################################
UBOOT_ROCKCHIP_VERSION = 1.3.3
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y)
	UBOOT_ROCKCHIP_SOURCE = u-boot-rk3288-v$(UBOOT_ROCKCHIP_VERSION).tar.gz
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3328),y)
	UBOOT_ROCKCHIP_SOURCE = u-boot-rk3328-v$(UBOOT_ROCKCHIP_VERSION).tar.gz
else
	# default to rk3399
	UBOOT_ROCKCHIP_SOURCE = u-boot-rk3399-v$(UBOOT_ROCKCHIP_VERSION).tar.gz
endif
UBOOT_ROCKCHIP_SITE = https://github.com/nuumio/u-boot-builder/releases/download/v$(UBOOT_ROCKCHIP_VERSION)

define UBOOT_ROCKCHIP_INSTALL_TARGET_CMDS
	mkdir -p   $(BINARIES_DIR)/u-boot-rockchip/
	cp -r $(@D)/* $(BINARIES_DIR)/u-boot-rockchip/
endef

$(eval $(generic-package))
