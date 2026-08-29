################################################################################
#
# libretro-bsnes-hd
#
################################################################################
# Version: Commits on Dec 5, 2025
LIBRETRO_BSNES_HD_VERSION = fc26b25ea236f0f877f0265d2a2c37dfd93dfde9
LIBRETRO_BSNES_HD_SITE = $(call github,DerKoun,bsnes-hd,$(LIBRETRO_BSNES_HD_VERSION))
LIBRETRO_BSNES_HD_LICENSE = GPLv3
LIBRETRO_BSNES_HD_DEPENDENCIES += retroarch
LIBRETRO_BSNES_HD_EMULATOR_INFO = bsnes_hd.libretro.core.yml

define LIBRETRO_BSNES_HD_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/bsnes -f GNUmakefile target="libretro" \
	    platform=linux compiler="$(TARGET_CXX)" local=false
endef

define LIBRETRO_BSNES_HD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bsnes/out/bsnes_hd_beta_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bsnes_hd_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))