################################################################################
#
# libretro-vitaquake2
#
################################################################################
# Version: Commits on Aug 10, 2022
LIBRETRO_VITAQUAKE2_VERSION = 59053244a03ed0f0976956365e60ca584fa6f162
LIBRETRO_VITAQUAKE2_SITE = $(call github,libretro,vitaquake2,$(LIBRETRO_VITAQUAKE2_VERSION))
LIBRETRO_VITAQUAKE2_LICENSE = GPL-2.0

LIBRETRO_VITAQUAKE2_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_VITAQUAKE2_PLATFORM=rpi4_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_VITAQUAKE2_PLATFORM=rpi3_64
endif

define LIBRETRO_VITAQUAKE2_BUILD_CMDS
	# build the mission cores
    $(foreach game,xatrix rogue zaero, \
	    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) clean && \
	    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) \
	        -f Makefile basegame=$(game) platform="$(LIBRETRO_VITAQUAKE2_PLATFORM)";
	)
	# now build the main core
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) clean && \
    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) \
	    -f Makefile platform="$(LIBRETRO_VITAQUAKE2_PLATFORM)"
endef

define LIBRETRO_VITAQUAKE2_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vitaquake2*.so \
		$(TARGET_DIR)/usr/lib/libretro/
endef

$(eval $(generic-package))
