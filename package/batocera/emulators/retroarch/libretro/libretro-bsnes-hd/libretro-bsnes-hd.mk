################################################################################
#
# libretro-bsnes-hd
#
################################################################################
# Version: Commits on Apr 26, 2023
LIBRETRO_BSNES_HD_VERSION = f46b6d6368ea93943a30b5d4e79e8ed51c2da5e8
LIBRETRO_BSNES_HD_SITE = $(call github,DerKoun,bsnes-hd,$(LIBRETRO_BSNES_HD_VERSION))
LIBRETRO_BSNES_HD_LICENSE = GPLv3

define LIBRETRO_BSNES_HD_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/bsnes -f GNUmakefile target="libretro" platform=linux compiler="$(TARGET_CXX)" local=false
endef

define LIBRETRO_BSNES_HD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bsnes/out/bsnes_hd_beta_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bsnes_hd_libretro.so
endef

$(eval $(generic-package))
