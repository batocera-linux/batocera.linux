################################################################################
#
# Sameduck
#
################################################################################
# Version.: Commits on Feb 27, 2023
LIBRETRO_SAMEDUCK_VERSION = e48eb3515d1056aa779e95946345dd9c6c6ef3a6
LIBRETRO_SAMEDUCK_SITE = $(call github,LIJI32,SameBoy,$(LIBRETRO_SAMEDUCK_VERSION))
LIBRETRO_SAMEDUCK_LICENSE = GPL-3.0

define LIBRETRO_SAMEDUCK_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libretro -f Makefile platform="unix"
endef

define LIBRETRO_SAMEDUCK_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/build/bin/sameduck_libretro.so \
    $(TARGET_DIR)/usr/lib/libretro/sameduck_libretro.so
endef

$(eval $(generic-package))
