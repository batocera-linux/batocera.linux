################################################################################
#
# libretro-mesen
#
################################################################################
# Version: Commits on Oct 21, 2024
LIBRETRO_MESEN_VERSION = 791c5e8153ee6e29691d45b5df2cf1151ff416f9
LIBRETRO_MESEN_SITE = $(call github,libretro,Mesen,$(LIBRETRO_MESEN_VERSION))
LIBRETRO_MESEN_LICENSE = GPL
LIBRETRO_MESEN_DEPENDENCIES += retroarch
LIBRETRO_MESEN_EMULATOR_INFO = mesen.libretro.core.yml

define LIBRETRO_MESEN_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    GIT_VERSION="" -C $(@D)/Libretro -f Makefile
endef

define LIBRETRO_MESEN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Libretro/mesen_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mesen_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))