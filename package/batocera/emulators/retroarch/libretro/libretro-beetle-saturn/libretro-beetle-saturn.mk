################################################################################
#
# BEETLE-SATURN
#
################################################################################
# Version.: Commits on Sep 11, 2019
LIBRETRO_BEETLE_SATURN_VERSION = 3313cc6760c14cffa9226e0cfd41debc11df8bdd
LIBRETRO_BEETLE_SATURN_SITE = $(call github,libretro,beetle-saturn-libretro,$(LIBRETRO_BEETLE_SATURN_VERSION))
LIBRETRO_BEETLE_SATURN_LICENSE = GPLv2

define LIBRETRO_BEETLE_SATURN_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" \
		RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D) -f Makefile HAVE_OPENGL=1 platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_SATURN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_saturn_hw_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/beetle-saturn_libretro.so
endef

$(eval $(generic-package))
