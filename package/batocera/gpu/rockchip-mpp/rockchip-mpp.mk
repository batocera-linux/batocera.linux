################################################################################
#
# rockchip-mpp
#
################################################################################

ROCKCHIP_MPP_VERSION = 1.0.7
ROCKCHIP_MPP_SITE = $(call github,rockchip-linux,mpp,$(ROCKCHIP_MPP_VERSION))
ROCKCHIP_MPP_LICENSE = Apache-2.0 & MIT
ROCKCHIP_MPP_LICENSE_FILES = LICENSES/Apache-2.0 & LICENSES/MIT
ROCKCHIP_MPP_INSTALL_STAGING = YES

ROCKCHIP_MPP_CONF_OPTS = \
	-DRKPLATFORM=ON \
	-DENABLE_AVSD=OFF \
	-DENABLE_H263D=OFF \
	-DENABLE_H264D=ON \
	-DENABLE_H265D=ON \
	-DENABLE_MPEG2D=ON \
	-DENABLE_MPEG4D=ON \
	-DENABLE_VP8D=ON \
	-DENABLE_JPEGD=OFF

ifeq ($(BR2_PACKAGE_LIBDRM),y)
    ROCKCHIP_MPP_CONF_OPTS += -DHAVE_DRM=ON
    ROCKCHIP_MPP_DEPENDENCIES = libdrm
endif

# Enable VP9 decoding for supported platforms
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3328)$(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
    ROCKCHIP_MPP_CONF_OPTS += -DENABLE_VP9D=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
    ROCKCHIP_MPP_CONF_OPTS += -DENABLE_VP9D=ON
else
    ROCKCHIP_MPP_CONF_OPTS += -DENABLE_VP9D=OFF
endif

$(eval $(cmake-package))
