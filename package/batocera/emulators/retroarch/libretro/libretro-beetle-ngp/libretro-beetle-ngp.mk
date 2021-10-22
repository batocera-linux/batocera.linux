################################################################################
#
# BEETLE_NGP
#
################################################################################
# Version.: Commits on Oct 15, 2021
LIBRETRO_BEETLE_NGP_VERSION = f969af2b52f20642aea7e800e3cfcce728f3aee9
LIBRETRO_BEETLE_NGP_SITE = $(call github,libretro,beetle-ngp-libretro,$(LIBRETRO_BEETLE_NGP_VERSION))
LIBRETRO_BEETLE_NGP_LICENSE = GPLv2

LIBRETRO_BEETLE_NGP_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_BEETLE_NGP_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_BEETLE_NGP_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
LIBRETRO_BEETLE_NGP_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_BEETLE_NGP_PLATFORM = rpi4_64
endif

define LIBRETRO_BEETLE_NGP_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_BEETLE_NGP_PLATFORM)"
endef

define LIBRETRO_BEETLE_NGP_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_ngp_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_ngp_libretro.so
endef

$(eval $(generic-package))
