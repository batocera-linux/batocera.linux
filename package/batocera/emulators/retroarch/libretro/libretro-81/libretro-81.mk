################################################################################
#
# ZX81
#
################################################################################
# Version.: Commits on Sep 17, 2019
LIBRETRO_81_VERSION = 4352130bd2363954262a804b086f86b9d13d97f9
LIBRETRO_81_SITE = $(call github,libretro,81-libretro,$(LIBRETRO_81_VERSION))
LIBRETRO_81_LICENSE = GPLv3

define LIBRETRO_81_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_81_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/81_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/81_libretro.so
endef

$(eval $(generic-package))
