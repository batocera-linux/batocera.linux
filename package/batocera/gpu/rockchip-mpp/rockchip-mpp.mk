################################################################################
#
# ROCKCHIP MPP
#
################################################################################

ROCKCHIP_MPP_VERSION = ad4fd32b2133ce622bd5635eb641beb5da18eae4
ROCKCHIP_MPP_SITE =  $(call github,rockchip-linux,mpp,$(ROCKCHIP_MPP_VERSION))
ROCKCHIP_MPP_INSTALL_STAGING = YES
ROCKCHIP_MPP_DEPENDENCIES = libdrm

ROCKCHIP_MPP_CONF_OPTS = -DENABLE_VP9D=ON -DRKPLATFORM=ON -DENABLE_AVSD=OFF \
-DENABLE_H263D=OFF -DENABLE_H264D=ON -DENABLE_H265D=ON -DENABLE_MPEG2D=ON \
-DENABLE_MPEG4D=ON -DENABLE_VP8D=ON -DENABLE_JPEGD=OFF -DHAVE_DRM=ON

$(eval $(cmake-package))
