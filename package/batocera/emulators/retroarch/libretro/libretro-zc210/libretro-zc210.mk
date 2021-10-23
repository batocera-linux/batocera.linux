################################################################################
#
# LIBRETRO ZC210
#
################################################################################
# Version.: Commits on Oct 12, 2021
LIBRETRO_ZC210_VERSION = bd32ba8834b082875fe753ffb01b707f47a91530
LIBRETRO_ZC210_SITE = https://github.com/netux79/zc210-libretro.git
LIBRETRO_ZC210_SITE_METHOD=git
LIBRETRO_ZC210_GIT_SUBMODULES=YES
LIBRETRO_ZC210_LICENSE = GPLv2
LIBRETRO_ZC210_DEPENDENCIES = retroarch

define LIBRETRO_ZC210_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="unix"
endef

define LIBRETRO_ZC210_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/zc210_libretro.so $(TARGET_DIR)/usr/lib/libretro/zc210_libretro.so
	$(INSTALL) -D $(@D)/datfile/zcdata.dat $(TARGET_DIR)/usr/share/batocera/datainit/bios
endef

$(eval $(generic-package))
