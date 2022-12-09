################################################################################
#
# libretro-fbalpha
#
################################################################################
# Version.: Commits on Mar 27, 2022
LIBRETRO_FBALPHA_VERSION = 7f8860543a81ba79c0e1ce1aa219af44568c628a
LIBRETRO_FBALPHA_SITE = $(call github,libretro,fbalpha2012,$(LIBRETRO_FBALPHA_VERSION))
LIBRETRO_FBALPHA_LICENSE = Non-commercial

LIBRETRO_FBALPHA_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_arm),y)
LIBRETRO_FBALPHA_PLATFORM = armv
endif

define LIBRETRO_FBALPHA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C \
        $(@D)/svn-current/trunk/ -f makefile.libretro platform="$(LIBRETRO_FBALPHA_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_FBALPHA_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_FBALPHA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/svn-current/trunk/fbalpha2012_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fbalpha_libretro.so
endef

$(eval $(generic-package))
