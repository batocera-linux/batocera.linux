################################################################################
#
# libretro-arduous
#
################################################################################

LIBRETRO_ARDUOUS_VERSION = aed5050
LIBRETRO_ARDUOUS_SITE = https://github.com/libretro/arduous.git
LIBRETRO_ARDUOUS_SITE_METHOD=git
LIBRETRO_ARDUOUS_GIT_SUBMODULES=YES
LIBRETRO_ARDUOUS_LICENSE = GPLv2

define LIBRETRO_ARDUOUS_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/arduous_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/arduous_libretro.so
endef

$(eval $(cmake-package))
