################################################################################
#
# MRBOOM
#
################################################################################
# Version.: Commits on Apr 2, 2020
LIBRETRO_MRBOOM_VERSION = b974ce0ae13a8a85835351670d64ca7cb16e7bbc
LIBRETRO_MRBOOM_SITE = $(call github,libretro,mrboom-libretro,$(LIBRETRO_MRBOOM_VERSION))
LIBRETRO_MRBOOM_LICENSE="GPLv2"

ifeq ($(BR2_ARM_FPU_NEON_VFPV4)$(BR2_ARM_FPU_NEON)$(BR2_ARM_FPU_NEON_FP_ARMV8),y)
    LIBRETRO_MRBOOM_EXTRA_ARGS = HAVE_NEON=1
endif

define LIBRETRO_MRBOOM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D)/ -f Makefile platform=unix $(LIBRETRO_MRBOOM_EXTRA_ARGS)
endef

define LIBRETRO_MRBOOM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mrboom_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mrboom_libretro.so
endef

$(eval $(generic-package))
