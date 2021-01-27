################################################################################
#
# mali-T760
#
################################################################################

MALI_T760_VERSION = 23dbb929bd339a6c9d8f6dc5ce348f60244cc040
MALI_T760_SITE = $(call github,rockchip-linux,libmali,$(MALI_T760_VERSION))
MALI_T760_INSTALL_STAGING = YES
MALI_T760_PROVIDES = libegl libgles

MALI_T760_CONF_OPTS += -Darch=auto -Dgpu=midgard-t76x -Dplatform=gbm -Dsubversion=all

$(eval $(meson-package))
