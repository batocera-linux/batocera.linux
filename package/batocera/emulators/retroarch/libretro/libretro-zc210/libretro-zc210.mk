################################################################################
#
# libretro-zc210
#
################################################################################
# Version: Commits on April 25, 2022
LIBRETRO_ZC210_VERSION = b6426da40b074245fda097fd345fa7c9cdbf152a
LIBRETRO_ZC210_SITE = https://github.com/netux79/zc210-libretro.git
LIBRETRO_ZC210_SITE_METHOD=git
LIBRETRO_ZC210_GIT_SUBMODULES=YES
LIBRETRO_ZC210_LICENSE = GPLv2
LIBRETRO_ZC210_DEPENDENCIES = retroarch

define LIBRETRO_ZC210_BUILD_CMDS
	$(ZC210_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="unix" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_ZC210_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_ZC210_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/zc210_libretro.so $(TARGET_DIR)/usr/lib/libretro/zc210_libretro.so
endef

$(eval $(generic-package))
