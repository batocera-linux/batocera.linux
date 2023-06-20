################################################################################
#
# ROCKCHIP_RGA
#
################################################################################
# Version.: Commits on May 29, 2023
ROCKCHIP_RGA_VERSION = f6e56e1378c50ddc85217a9c668649949ba50539
ROCKCHIP_RGA_SITE =  $(call github,JeffyCN,mirrors,linux-rga,$(ROCKCHIP_RGA_VERSION))

ROCKCHIP_RGA_LICENSE = Apache License 2.0
ROCKCHIP_RGA_DEPENDENCIES = libdrm

ROCKCHIP_RGA_INSTALL_STAGING = YES

$(eval $(meson-package))
