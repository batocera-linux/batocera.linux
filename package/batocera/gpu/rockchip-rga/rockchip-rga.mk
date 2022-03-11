################################################################################
#
# ROCKCHIP_RGA
#
################################################################################
# Version.: Commits on Aug 5, 2021
ROCKCHIP_RGA_VERSION = df26244eb0c3991df319d4276ab80e8c0bf91f64

ROCKCHIP_RGA_SOURCE = rockchip-rga-$(ROCKCHIP_RGA_VERSION).tar.gz
ROCKCHIP_RGA_SITE = https://github.com/batocera-linux/rockchip-packages/releases/download/20220303
#ROCKCHIP_RGA_SITE =  $(call github,rockchip-linux,linux-rga,$(ROCKCHIP_RGA_VERSION))

ROCKCHIP_RGA_LICENSE = Apache License 2.0
ROCKCHIP_RGA_DEPENDENCIES = libdrm

ROCKCHIP_RGA_INSTALL_STAGING = YES

$(eval $(meson-package))
