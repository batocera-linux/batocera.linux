################################################################################
#
# BEETLE-SATURN
#
################################################################################
LIBRETRO_BEETLE_SATURN_VERSION = #ceffed066ad14f894e2e11a25c20743399157000
LIBRETRO_BEETLE_SATURN_VERSION = bb5d0c126feb25cf980f5cc1fc57d6a5a6f6e7ab
LIBRETRO_BEETLE_SATURN_SITE = $(call github,libretro,beetle-saturn-libretro,$(LIBRETRO_BEETLE_SATURN_VERSION))

define LIBRETRO_BEETLE_SATURN_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D) -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_SATURN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_saturn_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/beetle-saturn_libretro.so
endef

$(eval $(generic-package))
