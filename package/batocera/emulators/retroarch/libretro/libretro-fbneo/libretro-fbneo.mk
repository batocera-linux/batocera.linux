################################################################################
#
# FBNEO
#
################################################################################
# Last revision: Aug 2, 2021
LIBRETRO_FBNEO_VERSION = 575020220899ca449a054217f5232926acc0bb35
LIBRETRO_FBNEO_SITE = $(call github,libretro,FBNeo,$(LIBRETRO_FBNEO_VERSION))
LIBRETRO_FBNEO_LICENSE = Non-commercial

ifeq ($(BR2_ARM_FPU_NEON_VFPV4)$(BR2_ARM_FPU_NEON)$(BR2_ARM_FPU_NEON_FP_ARMV8),y)
LIBRETRO_FBNEO_EXTRA_ARGS = HAVE_NEON=1 USE_CYCLONE=1 profile=performance
else
LIBRETRO_FBNEO_EXTRA_ARGS = HAVE_NEON=0 profile=accuracy
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86) $(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
LIBRETRO_FBNEO_EXTRA_ARGS = USE_X64_DRC=1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326_ANY),y)
LIBRETRO_FBNEO_EXTRA_ARGS = USE_EXPERIMENTAL_FLAGS=0
endif

define LIBRETRO_FBNEO_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/src/burner/libretro -f Makefile platform="$(LIBRETRO_PLATFORM)" $(LIBRETRO_FBNEO_EXTRA_ARGS) \
        GIT_VERSION=" $(shell echo $(LIBRETRO_FBNEO_VERSION) | cut -c 1-10)"
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
