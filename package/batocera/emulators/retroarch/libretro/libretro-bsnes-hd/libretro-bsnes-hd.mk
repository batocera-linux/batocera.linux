################################################################################
#
# BSNES-HD
#
################################################################################
# Version.: Commits on Jun 18, 2021
LIBRETRO_BSNES_HD_VERSION = 0fd18e0f5767284fd373aebd75b00b5bab0d44a9
LIBRETRO_BSNES_HD_SITE = $(call github,DerKoun,bsnes-hd,$(LIBRETRO_BSNES_HD_VERSION))
LIBRETRO_BSNES_HD_LICENSE = GPLv3

define LIBRETRO_BSNES_HD_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/bsnes -f GNUmakefile target="libretro" platform=linux local=false
endef

define LIBRETRO_BSNES_HD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bsnes/out/bsnes_hd_beta_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bsnes_hd_libretro.so
endef

$(eval $(generic-package))
