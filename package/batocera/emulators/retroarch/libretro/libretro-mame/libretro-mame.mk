################################################################################
#
# MAME
#
################################################################################
# Version.: Commits on Nov 10, 2018 (0.203)
LIBRETRO_MAME_VERSION = 1347e1cf946e8402164acaaea1e12e08de6ca14d
LIBRETRO_MAME_SITE = $(call github,libretro,mame,$(LIBRETRO_MAME_VERSION))

# x86
ifeq ($(BR2_x86_i586),y)
	LIBRETRO_MAME_PLATFORM = PTR64=0
endif

# x86_64
ifeq ($(BR2_x86_64),y)
	LIBRETRO_MAME_PLATFORM = PTR64=1
endif

define LIBRETRO_MAME_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_MAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame_libretro.so
endef

$(eval $(generic-package))
