################################################################################
#
# libretro-arduous
#
################################################################################
# Version: Commits on May 14, 2024
LIBRETRO_ARDUOUS_VERSION = 50c1e48084f003dee582ed5f4f5c0f59eb30bc4c
LIBRETRO_ARDUOUS_SITE = https://github.com/libretro/arduous.git
LIBRETRO_ARDUOUS_SITE_METHOD=git
LIBRETRO_ARDUOUS_GIT_SUBMODULES=YES
LIBRETRO_ARDUOUS_LICENSE = GPLv2

define LIBRETRO_ARDUOUS_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/arduous_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/arduous_libretro.so
endef

$(eval $(cmake-package))
