################################################################################
#
# IMAME
#
################################################################################
# Version.: Commits on Jan 12, 2020
LIBRETRO_IMAME_VERSION = e5d4a934c60adc6d42a3f87319312aad89595a15
LIBRETRO_IMAME_SITE = $(call github,libretro,mame2000-libretro,$(LIBRETRO_IMAME_VERSION))
LIBRETRO_IMAME_LICENSE = MAME

define LIBRETRO_IMAME_BUILD_CMDS
	mkdir -p $(@D)/obj_libretro_libretro/cpu
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" -C $(@D) -f Makefile ARM=1
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
