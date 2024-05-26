################################################################################
#
# ROCKCHIP_RGA
#
################################################################################

# RK3326 needs the older rockchip-rga for it's 4.4 kernel
ifeq ($(BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_4_4),y)
    # Version.: Commits on Aug 5, 2021
    ROCKCHIP_RGA_VERSION = df26244eb0c3991df319d4276ab80e8c0bf91f64
    ROCKCHIP_RGA_SOURCE = rockchip-rga-$(ROCKCHIP_RGA_VERSION).tar.gz
    ROCKCHIP_RGA_SITE = https://github.com/batocera-linux/rockchip-packages/releases/download/20220303
else
    # Version.: Commits on May 29, 2023
    ROCKCHIP_RGA_VERSION = f6e56e1378c50ddc85217a9c668649949ba50539
    ROCKCHIP_RGA_SITE =  $(call github,JeffyCN,mirrors,linux-rga,$(ROCKCHIP_RGA_VERSION))
endif

ROCKCHIP_RGA_LICENSE = Apache License 2.0
ROCKCHIP_RGA_DEPENDENCIES = libdrm

ROCKCHIP_RGA_INSTALL_STAGING = YES

$(eval $(meson-package))
