################################################################################
#
# rockchip-rga
#
################################################################################

# RK3326 needs the older rockchip-rga for it's 4.4 kernel
ifeq ($(BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_4_4),y)
    # Version: Commits on Aug 5, 2021
    ROCKCHIP_RGA_VERSION = df26244eb0c3991df319d4276ab80e8c0bf91f64
    ROCKCHIP_RGA_SOURCE = rockchip-rga-$(ROCKCHIP_RGA_VERSION).tar.gz
    ROCKCHIP_RGA_SITE = https://github.com/batocera-linux/rockchip-packages/releases/download/20220303
else
    # Version: Commits on Sep 19, 2024
    ROCKCHIP_RGA_VERSION = e97e327662d1c0867d4cbcc01d5caf15250fc4e7
    ROCKCHIP_RGA_SITE =  $(call github,nyanmisaka,rk-mirrors,jellyfin-rga,$(ROCKCHIP_RGA_VERSION))
endif

ROCKCHIP_RGA_LICENSE = Apache License 2.0
ROCKCHIP_RGA_LICENSE_FILE = COPYING

ifeq ($(BR2_PACKAGE_LIBDRM),y)
    ROCKCHIP_RGA_DEPENDENCIES = libdrm
    ROCKCHIP_RGA_CONF_OPTS += -Dlibdrm=true
endif

ROCKCHIP_RGA_INSTALL_STAGING = YES

$(eval $(meson-package))
