################################################################################
#
# MAME
#
################################################################################
# Version.: Commits on Feb 2, 2019 (0.206)
LIBRETRO_MAME_VERSION = a7f6d0d690f9dad84878dbe01bfcbb88b19493f1
LIBRETRO_MAME_SITE = $(call github,libretro,mame,$(LIBRETRO_MAME_VERSION))
LIBRETRO_MAME_LICENSE="MAME"

ifeq ($(BR2_x86_i586),y)
	LIBRETRO_MAME_EXTRA_ARGS = PTR64=0
else
	LIBRETRO_MAME_EXTRA_ARGS = PTR64=1
endif

define LIBRETRO_MAME_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile.libretro $(LIBRETRO_MAME_EXTRA_ARGS) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_MAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame_libretro.so
endef

$(eval $(generic-package))
