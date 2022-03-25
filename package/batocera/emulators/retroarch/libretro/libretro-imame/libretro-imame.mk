################################################################################
#
# libretro-imame
#
################################################################################
# Version: Commits on Feb 22, 2022
LIBRETRO_IMAME_VERSION = 098df85e3bc04a74db8c810d51fb72879594dc40
LIBRETRO_IMAME_SITE = $(call github,libretro,mame2000-libretro,$(LIBRETRO_IMAME_VERSION))
LIBRETRO_IMAME_LICENSE = MAME

LIBRETRO_IMAME_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_IMAME_PLATFORM = rpi1
endif

define LIBRETRO_IMAME_BUILD_CMDS
	mkdir -p $(@D)/obj_libretro_libretro/cpu
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_IMAME_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_IMAME_VERSION) | cut -c 1-7)"
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
