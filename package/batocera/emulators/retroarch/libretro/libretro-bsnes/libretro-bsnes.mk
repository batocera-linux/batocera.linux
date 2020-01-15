################################################################################
#
# BSNES
#
################################################################################
# Version.: Commits on Jan 08, 2020
LIBRETRO_BSNES_VERSION = 55e78b03deb7c4104580dec9593ac0e861d684e9
LIBRETRO_BSNES_SITE = $(call github,byuu,bsnes,$(LIBRETRO_BSNES_VERSION))
LIBRETRO_BSNES_LICENSE = GPLv3

define LIBRETRO_BSNES_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" \
		CC="$(TARGET_CC)" -C $(@D)/bsnes -f GNUmakefile target="libretro" platform=linux
endef

define LIBRETRO_BSNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bsnes/out/bsnes_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bsnes_libretro.so
endef

$(eval $(generic-package))
