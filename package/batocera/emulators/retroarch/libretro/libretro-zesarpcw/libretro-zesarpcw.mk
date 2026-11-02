################################################################################
#
# libretro-zesarpcw
#
################################################################################
# Version: Commits on Oct 3, 2026
LIBRETRO_ZESARPCW_VERSION = 23af8913c0ff22b9d89646ca9f98660db17f0057
LIBRETRO_ZESARPCW_SITE = $(call github,retrodiv,ZEsarPCW-libretro,$(LIBRETRO_ZESARPCW_VERSION))
LIBRETRO_ZESARPCW_LICENSE = GPL-3.0, MIT
LIBRETRO_ZESARPCW_LICENSE_FILES = LICENSE sources/openpcw-os/LICENSE \
	sources/openpcw-os/LICENSE.microsoft-msdos
LIBRETRO_ZESARPCW_DEPENDENCIES = retroarch
LIBRETRO_ZESARPCW_EMULATOR_INFO = zesarpcw.libretro.core.yml

define LIBRETRO_ZESARPCW_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CC="$(TARGET_CC)" \
		-C $(@D) -f Makefile platform=unix
endef

define LIBRETRO_ZESARPCW_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/zesarpcw_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/zesarpcw_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
