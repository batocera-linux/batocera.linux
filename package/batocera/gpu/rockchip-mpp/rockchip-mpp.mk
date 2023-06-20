################################################################################
#
# ROCKCHIP MPP
#
################################################################################
# Version.: Commits on May 18, 2023
ROCKCHIP_MPP_VERSION = e025b079a2b01aadc09b0da118b9509c2f02dc6c
ROCKCHIP_MPP_SITE =  $(call github,rockchip-linux,mpp,$(ROCKCHIP_MPP_VERSION))
ROCKCHIP_MPP_LICENSE = Apache License 2.0
ROCKCHIP_MPP_DEPENDENCIES = libdrm

ROCKCHIP_MPP_INSTALL_STAGING = YES

ifneq (,$(findstring rk3328,$(BR2_LINUX_KERNEL_INTREE_DTS_NAME)))
	ROCKCHIP_MPP_CONF_OPTS +=-DENABLE_VP9D=ON
else ifneq (,$(findstring rk3399,$(BR2_LINUX_KERNEL_INTREE_DTS_NAME)))
	ROCKCHIP_MPP_CONF_OPTS +=-DENABLE_VP9D=ON
else ifneq (,$(findstring rk3588,$(BR2_LINUX_KERNEL_INTREE_DTS_NAME)))
	ROCKCHIP_MPP_CONF_OPTS +=-DENABLE_VP9D=ON
else
	ROCKCHIP_MPP_CONF_OPTS +=-DENABLE_VP9D=OFF
endif

ROCKCHIP_MPP_CONF_OPTS += -DRKPLATFORM=ON -DENABLE_AVSD=OFF -DENABLE_H263D=OFF \
	-DENABLE_H264D=ON -DENABLE_H265D=ON -DENABLE_MPEG2D=ON -DENABLE_MPEG4D=ON \
	-DENABLE_VP8D=ON -DENABLE_JPEGD=OFF -DHAVE_DRM=ON

$(eval $(cmake-package))
