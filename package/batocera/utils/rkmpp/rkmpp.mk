################################################################################
#
# rkmpp
#
################################################################################

RKMPP_VERSION = 313156e18b63c6773ea1b466ad08560857860053
RKMPP_SITE = $(call github,rockchip-linux,mpp,$(RKMPP_VERSION))
RKMPP_LICENSE = APL
RKMPP_DEPENDENCIES = libdrm
RKMPP_INSTALL_STAGING = YES

ifneq (,$(findstring rk3328,$(BR2_LINUX_KERNEL_INTREE_DTS_NAME)))
	RKMPP_CONF_OPTS +=-DENABLE_VP9D=ON
else
	ifneq (,$(findstring rk3399,$(BR2_LINUX_KERNEL_INTREE_DTS_NAME)))
		RKMPP_CONF_OPTS +=-DENABLE_VP9D=ON
	else
		RKMPP_CONF_OPTS +=-DENABLE_VP9D=OFF
	endif
endif


RKMPP_CONF_OPTS += \
	-DRKPLATFORM=ON \
	-DENABLE_AVSD=OFF \
	-DENABLE_H263D=OFF \
	-DENABLE_H264D=ON \
	-DENABLE_H265D=ON \
	-DENABLE_MPEG2D=ON \
	-DENABLE_MPEG4D=ON \
	-DENABLE_VP8D=ON \
	-DENABLE_JPEGD=OFF \
	-DHAVE_DRM=ON

$(eval $(cmake-package))
