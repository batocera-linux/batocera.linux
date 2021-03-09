################################################################################
#
# mali-T860
#
################################################################################

MALI_T860_VERSION = 6141ad6e6f2d3eb38e7e0962f61b78510b2e2d2c
MALI_T860_SITE = $(call github,rockchip-linux,libmali,$(MALI_T860_VERSION))
MALI_T860_INSTALL_STAGING = YES
MALI_T860_PROVIDES = libegl libgles libmali

MALI_T860_CONF_OPTS += -Darch=auto -Dgpu=midgard-t86x -Dversion=r18p0 -Dplatform=gbm

$(eval $(meson-package))
