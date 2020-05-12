################################################################################
#
# PCSXREARMED
#
################################################################################
# Version.: Commits on May 02, 2020
LIBRETRO_PCSX_VERSION = 14e45ca252a6b0bcd0863310b862538eb3af8aee
LIBRETRO_PCSX_SITE = $(call github,libretro,pcsx_rearmed,$(LIBRETRO_PCSX_VERSION))
LIBRETRO_PCSX_LICENSE = GPLv2

LIBRETRO_PCSX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	LIBRETRO_PCSX_PLATFORM = CortexA73_G12B
endif

define LIBRETRO_PCSX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_PCSX_PLATFORM)"
endef

define LIBRETRO_PCSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/pcsx_rearmed_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcsx_rearmed_libretro.so
endef

$(eval $(generic-package))
