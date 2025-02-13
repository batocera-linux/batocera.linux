################################################################################
#
# libretro-bsnes-hd
#
################################################################################
# Version: Commits on Oct 22, 2024
LIBRETRO_BSNES_HD_VERSION = 0bb7b8645e22ea2476cabd58f32e987b14686601
LIBRETRO_BSNES_HD_SITE = $(call github,DerKoun,bsnes-hd,$(LIBRETRO_BSNES_HD_VERSION))
LIBRETRO_BSNES_HD_LICENSE = GPLv3
LIBRETRO_BSNES_HD_DEPENDENCIES += retroarch

define LIBRETRO_BSNES_HD_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/bsnes -f GNUmakefile target="libretro" \
	    platform=linux compiler="$(TARGET_CXX)" local=false
endef

define LIBRETRO_BSNES_HD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bsnes/out/bsnes_hd_beta_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bsnes_hd_libretro.so
endef

$(eval $(generic-package))
