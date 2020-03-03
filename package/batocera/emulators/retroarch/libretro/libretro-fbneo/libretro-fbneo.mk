################################################################################
#
# FBNEO
#
################################################################################
# Version.: Commits on Feb 05, 2020
LIBRETRO_FBNEO_VERSION = 539cb5f07ebb16a196919b453cd02c5b689091d1
LIBRETRO_FBNEO_SITE = $(call github,libretro,FBNeo,$(LIBRETRO_FBNEO_VERSION))
LIBRETRO_FBNEO_LICENSE = Non-commercial

ifeq ($(BR2_ARM_FPU_NEON_VFPV4)$(BR2_ARM_FPU_NEON)$(BR2_ARM_FPU_NEON_FP_ARMV8),y)
    LIBRETRO_FBNEO_EXTRA_ARGS = HAVE_NEON=1 profile=performance
else
    LIBRETRO_FBNEO_EXTRA_ARGS = HAVE_NEON=0 profile=accuracy
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86) $(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	 LIBRETRO_FBNEO_EXTRA_ARGS = USE_X64_DRC=1
endif

define LIBRETRO_FBNEO_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" \
		AR="$(TARGET_AR)" -C $(@D)/src/burner/libretro -f Makefile platform="$(LIBRETRO_PLATFORM)" $(LIBRETRO_FBNEO_EXTRA_ARGS)
endef

define LIBRETRO_FBNEO_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/burner/libretro/fbneo_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fbneo_libretro.so

	# Bios
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/fbneo/samples
	$(INSTALL) -D $(@D)/metadata/* \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios/fbneo

    # Need to think of another way to use these files.
    # They take up a lot of space on tmpfs.
	$(INSTALL) -D $(@D)/dats/* \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios/fbneo	
endef

$(eval $(generic-package))
