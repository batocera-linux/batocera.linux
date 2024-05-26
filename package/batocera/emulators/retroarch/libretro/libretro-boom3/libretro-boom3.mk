################################################################################
#
# libretro-boom3
#
################################################################################
# Version: Commits on Aug 10, 2022
LIBRETRO_BOOM3_VERSION = 0bea79abf5ec8262dfe9af73cb8c54ea6e2aeb98
LIBRETRO_BOOM3_SITE = $(call github,libretro,boom3,$(LIBRETRO_BOOM3_VERSION))
LIBRETRO_BOOM3_LICENSE = GPLv3
LIBRETRO_BOOM3_LICENSE_FILES = COPYING.txt
LIBRETRO_BOOM3_SUBDIR = neo

LIBRETRO_BOOM3_DEPENDENCIES = host-libjpeg libcurl libogg libvorbis openal sdl2 zlib 

LIBRETRO_BOOM3_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_BOOM3_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/neo -f Makefile platform="$(LIBRETRO_BOOM3_PLATFORM)" \
		GIT_VERSION="-$(shell echo $(LIBRETRO_BOOM3_VERSION) | cut -c 1-7)"
	# boom3 XP core
    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/neo -f Makefile D3XP=1 platform="$(LIBRETRO_BOOM3_PLATFORM)" \
		GIT_VERSION="-$(shell echo $(LIBRETRO_BOOM3_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BOOM3_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/neo/boom3_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/boom3_libretro.so
	$(INSTALL) -D $(@D)/neo/boom3_xp_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/boom3_xp_libretro.so
endef

$(eval $(generic-package))
