################################################################################
#
# Sameduck
#
################################################################################
# Version.: Commits on Dec 10, 2023
# This is the latest on the SameDuck branch of the SameBoy emulator (used here for Megaduck)
LIBRETRO_SAMEDUCK_BRANCH = SameDuck
LIBRETRO_SAMEDUCK_VERSION = 5619abdb01cee6bedb47599cdb5532c318443b52
LIBRETRO_SAMEDUCK_SITE = $(call github,LIJI32,SameBoy,$(LIBRETRO_SAMEDUCK_VERSION))
LIBRETRO_SAMEDUCK_LICENSE = GPL-3.0
LIBRETRO_SAMEDUCK_DEPENDENCIES += retroarch
LIBRETRO_SAMEDUCK_EMULATOR_INFO = sameduck.libretro.core.yml

define LIBRETRO_SAMEDUCK_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libretro -f Makefile platform="unix"
endef

define LIBRETRO_SAMEDUCK_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/build/bin/sameduck_libretro.so \
    $(TARGET_DIR)/usr/lib/libretro/sameduck_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))