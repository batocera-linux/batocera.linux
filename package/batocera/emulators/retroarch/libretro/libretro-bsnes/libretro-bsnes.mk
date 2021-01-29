################################################################################
#
# BSNES
#
################################################################################
# Version.: Commits on Oct 13, 2020
LIBRETRO_BSNES_VERSION = d639034a074cd88ce130d6b4956d7d8fff9431cf
LIBRETRO_BSNES_SITE = $(call github,libretro,bsnes,$(LIBRETRO_BSNES_VERSION))
LIBRETRO_BSNES_LICENSE = GPLv3

define LIBRETRO_BSNES_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/bsnes -f GNUmakefile target="libretro" platform=linux local=false
endef

define LIBRETRO_BSNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bsnes/out/bsnes_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bsnes_libretro.so
endef

$(eval $(generic-package))
