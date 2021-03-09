################################################################################
#
# tic80 - TIC-80 emulator
#
################################################################################
# Version.: Commits on Jan 29, 2021
#LIBRETRO_TIC80_VERSION = acddaaad3ae5f5f403db9f1a69872697fb49efb5
#LIBRETRO_TIC80_SITE = https://github.com/nesbox/TIC-80.git
#LIBRETRO_TIC80_SITE_METHOD=git
#LIBRETRO_TIC80_GIT_SUBMODULES=YES

# temporary access
LIBRETRO_TIC80_VERSION = acddaaad3ae5f5f403db9f1a69872697fb49efb5
LIBRETRO_TIC80_SOURCE = TIC-80-$(LIBRETRO_TIC80_VERSION).tar.gz
LIBRETRO_TIC80_SITE = https://batocera.org/packages

LIBRETRO_TIC80_LICENSE = MIT
LIBRETRO_TIC80_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_TIC80_PLATFORM = rpi3
endif

LIBRETRO_TIC80_CONF_OPTS += -DBUILD_PLAYER=OFF -DBUILD_SOKOL=OFF -DBUILD_SDL=OFF -DBUILD_DEMO_CARTS=OFF -DBUILD_LIBRETRO=ON

define LIBRETRO_TIC80_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_TIC80_PLATFORM)"
endef

define LIBRETRO_TIC80_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/lib/tic80_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/tic80_libretro.so
endef

$(eval $(cmake-package))
