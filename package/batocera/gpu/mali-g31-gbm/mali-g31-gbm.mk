################################################################################
#
# mali-g31-gbm
#
################################################################################
# Version.: Commits on Jan 19, 2021
MALI_G31_GBM_VERSION = 55b5d650efc98db2ce2e7a170111a71cf0e2c239
MALI_G31_GBM_SITE = $(call github,rockchip-linux,libmali,$(MALI_G31_GBM_VERSION))

MALI_G31_GBM_INSTALL_STAGING = YES
MALI_G31_GBM_PROVIDES = libegl libgles

MALI_G31_GBM_CONF_OPTS = \
	-Dplatform=gbm \
	-Dgpu=bifrost-g31 \
	-Dversion=rxp0

$(eval $(meson-package))
