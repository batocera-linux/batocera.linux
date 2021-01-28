################################################################################
#
# mali-T760
#
################################################################################

MALI_T760_VERSION = 6141ad6e6f2d3eb38e7e0962f61b78510b2e2d2c
MALI_T760_SITE = $(call github,rockchip-linux,libmali,$(MALI_T760_VERSION))
MALI_T760_INSTALL_STAGING = YES
MALI_T760_PROVIDES = libegl libgles libmali

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_MIQI),y)
MALI_T760_CONF_OPTS += -Darch=auto -Dgpu=midgard-t76x -Dversion=r18p0-r1p0 -Dsubversion=all -Dplatform=gbm
else
MALI_T760_CONF_OPTS += -Darch=auto -Dgpu=midgard-t76x -Dplatform=gbm -Dsubversion=all
endif

$(eval $(meson-package))
