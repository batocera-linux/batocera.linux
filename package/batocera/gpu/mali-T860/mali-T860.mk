################################################################################
#
# mali-T860
#
################################################################################
# Version.: Commits on Jun 11, 2021
MALI_T860_VERSION = ad4c28932c3d07c75fc41dd4a3333f9013a25e7f

MALI_T860_SOURCE = libmali-$(MALI_T860_VERSION).tar.gz
MALI_T860_SITE = https://github.com/batocera-linux/rockchip-packages/releases/download/20220303
#MALI_T860_SITE = $(call github,rockchip-linux,libmali,$(MALI_T860_VERSION))

MALI_T860_DEPENDENCIES = libdrm

MALI_T860_INSTALL_STAGING = YES
MALI_T860_PROVIDES = libegl libgles libmali

MALI_T860_CONF_OPTS += -Darch=auto -Dgpu=midgard-t86x -Dversion=r18p0 -Dplatform=gbm -Dkhr-header=true

$(eval $(meson-package))
