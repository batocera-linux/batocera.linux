################################################################################
#
# libretro-arduous
#
################################################################################
# Version: Commits on Oct 10, 2024
LIBRETRO_ARDUOUS_VERSION = 2273b485628790a2ce954941341b5b071c3fb30e
LIBRETRO_ARDUOUS_SITE = https://github.com/libretro/arduous.git
LIBRETRO_ARDUOUS_SITE_METHOD=git
LIBRETRO_ARDUOUS_GIT_SUBMODULES=YES
LIBRETRO_ARDUOUS_LICENSE = GPLv2

define LIBRETRO_ARDUOUS_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/arduous_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/arduous_libretro.so
endef

$(eval $(cmake-package))
