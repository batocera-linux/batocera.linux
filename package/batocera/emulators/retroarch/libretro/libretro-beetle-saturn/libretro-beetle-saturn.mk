################################################################################
#
# libretro-beetle-saturn
#
################################################################################
# Version: Commits on Aug 11, 2026
LIBRETRO_BEETLE_SATURN_VERSION = ed549bdac0e1a830bb794fa720e45c225a45355c
LIBRETRO_BEETLE_SATURN_SITE = \
    $(call github,libretro,beetle-saturn-libretro,$(LIBRETRO_BEETLE_SATURN_VERSION))
LIBRETRO_BEETLE_SATURN_LICENSE = GPLv2
LIBRETRO_BEETLE_SATURN_DEPENDENCIES += retroarch
LIBRETRO_BEETLE_SATURN_EMULATOR_INFO = beetle-saturn.libretro.core.yml

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
LIBRETRO_BEETLE_SATURN_DEPENDENCIES += libgles
endif

define LIBRETRO_BEETLE_SATURN_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D) -f Makefile HAVE_OPENGL=1 platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_SATURN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_saturn_hw_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/beetle-saturn_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
