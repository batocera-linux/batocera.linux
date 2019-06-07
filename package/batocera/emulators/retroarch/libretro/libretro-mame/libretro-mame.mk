################################################################################
#
# MAME
#
################################################################################
# Version.: Commits on Apr 30, 2019 (0.209)
LIBRETRO_MAME_VERSION = 47c241e4f528f663a36ae82a3bbaa789d929e282
LIBRETRO_MAME_SITE = $(call github,libretro,mame,$(LIBRETRO_MAME_VERSION))
LIBRETRO_MAME_LICENSE = MAME

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
