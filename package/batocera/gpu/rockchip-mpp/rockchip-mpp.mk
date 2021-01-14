################################################################################
#
# ROCKCHIP MPP
#
################################################################################

ROCKCHIP_MPP_VERSION = dbd5ae409938d0951dad17a4a229c4f4156c0db3
#ROCKCHIP_MPP_SITE =  $(call github,rockchip-linux,mpp,$(ROCKCHIP_MPP_VERSION))
ROCKCHIP_MPP_SITE =  $(call github,batocera-linux,mpp,$(ROCKCHIP_MPP_VERSION))
ROCKCHIP_MPP_INSTALL_STAGING = YES
ROCKCHIP_MPP_DEPENDENCIES = libdrm

ifneq (,$(findstring rk3328,$(BR2_LINUX_KERNEL_INTREE_DTS_NAME)))
	ROCKCHIP_MPP_CONF_OPTS +=-DENABLE_VP9D=ON
else
	ifneq (,$(findstring rk3399,$(BR2_LINUX_KERNEL_INTREE_DTS_NAME)))
		ROCKCHIP_MPP_CONF_OPTS +=-DENABLE_VP9D=ON
	else
		ROCKCHIP_MPP_CONF_OPTS +=-DENABLE_VP9D=OFF
	endif
endif

ROCKCHIP_MPP_CONF_OPTS += -DRKPLATFORM=ON -DENABLE_AVSD=OFF -DENABLE_H263D=OFF \
	-DENABLE_H264D=ON -DENABLE_H265D=ON -DENABLE_MPEG2D=ON -DENABLE_MPEG4D=ON \
	-DENABLE_VP8D=ON -DENABLE_JPEGD=OFF -DHAVE_DRM=ON

$(eval $(cmake-package))
