################################################################################
#
# MAME
#
################################################################################
# Version.: Commits on Mar 3, 2019 (0.207)
LIBRETRO_MAME_VERSION = dd899f5c63ce1d725d23706c1d882c58738d8f3c
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

define LIBRETRO_MAME_LIBM_FIXUP
        $(SED) s+-lm+$(STAGING_DIR)/usr/lib/libm.a+ $(@D)/3rdparty/genie/build/gmake.linux/genie.make
endef
LIBRETRO_MAME_PRE_CONFIGURE_HOOKS += LIBRETRO_MAME_LIBM_FIXUP

$(eval $(generic-package))
