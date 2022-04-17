################################################################################
#
# libretro-vice
#
################################################################################
# Version: Commits on Apr 16, 2022
LIBRETRO_VICE_VERSION = ae17f2c75a7f8f6d49d5d0c5a197157364a513b1
LIBRETRO_VICE_SITE = $(call github,libretro,vice-libretro,$(LIBRETRO_VICE_VERSION))
LIBRETRO_VICE_LICENSE = GPLv2

LIBRETRO_VICE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_VICE_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_VICE_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_VICE_PLATFORM = rpi3
    else
        LIBRETRO_VICE_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_VICE_PLATFORM = rpi4_64

else ifeq ($(BR2_arm),y)
LIBRETRO_VICE_PLATFORM = armv neon

else ifeq ($(BR2_aarch64),y)
LIBRETRO_VICE_PLATFORM = unix
endif

define LIBRETRO_VICE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_VICE_PLATFORM)" EMUTYPE=x64
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile objectclean
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_VICE_PLATFORM)" EMUTYPE=x64sc
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile objectclean
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_VICE_PLATFORM)" EMUTYPE=x128
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile objectclean
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_VICE_PLATFORM)" EMUTYPE=xpet
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile objectclean
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_VICE_PLATFORM)" EMUTYPE=xplus4
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile objectclean
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_VICE_PLATFORM)" EMUTYPE=xvic
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile objectclean
endef

define LIBRETRO_VICE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vice_x64_libretro.so $(TARGET_DIR)/usr/lib/libretro/vice_x64_libretro.so
	$(INSTALL) -D $(@D)/vice_x64sc_libretro.so $(TARGET_DIR)/usr/lib/libretro/vice_x64sc_libretro.so
	$(INSTALL) -D $(@D)/vice_x128_libretro.so $(TARGET_DIR)/usr/lib/libretro/vice_x128_libretro.so
	$(INSTALL) -D $(@D)/vice_xpet_libretro.so $(TARGET_DIR)/usr/lib/libretro/vice_xpet_libretro.so
	$(INSTALL) -D $(@D)/vice_xplus4_libretro.so $(TARGET_DIR)/usr/lib/libretro/vice_xplus4_libretro.so
	$(INSTALL) -D $(@D)/vice_xvic_libretro.so $(TARGET_DIR)/usr/lib/libretro/vice_xvic_libretro.so
endef

$(eval $(generic-package))
