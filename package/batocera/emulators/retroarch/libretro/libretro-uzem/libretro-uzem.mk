################################################################################
#
# Uzem - an Uzebox emulator (retro-minimalist 8-bit opensource console)
#
################################################################################
# Version.: Commits on Mar 14, 2021
LIBRETRO_UZEM_VERSION = 675b4485b776fe5166612192466c95a25a927a63
LIBRETRO_UZEM_SITE = $(call github,libretro,libretro-uzem,$(LIBRETRO_UZEM_VERSION))
LIBRETRO_UZEM_LICENSE = MIT

LIBRETRO_UZEM_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_UZEM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_UZEM_PLATFORM)"
endef

define LIBRETRO_UZEM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/uzem_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/uzem_libretro.so
endef

$(eval $(generic-package))
