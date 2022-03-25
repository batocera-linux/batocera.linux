################################################################################
#
# libretro-superflappybirds
#
################################################################################
# Version.: Commits on Feb 18, 2019
LIBRETRO_SUPERFLAPPYBIRDS_VERSION = 0ba0e188cae44c8900a2f5a04577de85dc8c4410
LIBRETRO_SUPERFLAPPYBIRDS_SITE = $(call github,IgniparousTempest,libretro-superflappybirds,$(LIBRETRO_SUPERFLAPPYBIRDS_VERSION))

LIBRETRO_SUPERFLAPPYBIRDS_LICENSE = GPL-3.0

LIBRETRO_SUPERFLAPPYBIRDS_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_SUPERFLAPPYBIRDS_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release

LIBRETRO_SUPERFLAPPYBIRDS_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_SUPERFLAPPYBIRDS_INSTALL_TARGET_CMDS
		cp -r $(@D)/resources $(TARGET_DIR)/usr/lib/libretro
        $(INSTALL) -D $(@D)/buildroot-build/superflappybirds_libretro.so \
                $(TARGET_DIR)/usr/lib/libretro/superflappybirds_libretro.so
endef

$(eval $(cmake-package))
