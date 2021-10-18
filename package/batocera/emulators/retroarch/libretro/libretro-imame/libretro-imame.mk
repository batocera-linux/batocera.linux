################################################################################
#
# IMAME
#
################################################################################
# Version.: Commits on Oct 11, 2021
LIBRETRO_IMAME_VERSION = 4793742b457945afb74053c8a895e6ff0b36b033
LIBRETRO_IMAME_SITE = $(call github,libretro,mame2000-libretro,$(LIBRETRO_IMAME_VERSION))
LIBRETRO_IMAME_LICENSE = MAME

LIBRETRO_IMAME_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_IMAME_PLATFORM = rpi1
endif

define LIBRETRO_IMAME_BUILD_CMDS
	mkdir -p $(@D)/obj_libretro_libretro/cpu
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_IMAME_PLATFORM)"
endef

define LIBRETRO_IMAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame2000_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/imame4all_libretro.so

	# Bios
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/imame4all/samples
	$(INSTALL) -D $(@D)/metadata/* \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios/imame4all
endef

$(eval $(generic-package))
