################################################################################
#
# CHAILOVE
#
################################################################################
# Version.: Commits on Aug 01, 2021
LIBRETRO_CHAILOVE_VERSION = e300ec2c96cff9d4ba678a283d2faef0cf3b48ff
LIBRETRO_CHAILOVE_SITE = https://github.com/libretro/libretro-chailove.git

LIBRETRO_CHAILOVE_SITE_METHOD=git
LIBRETRO_CHAILOVE_GIT_SUBMODULES=YES
LIBRETRO_CHAILOVE_LICENSE = MIT

define LIBRETRO_CHAILOVE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="unix"
endef

define LIBRETRO_CHAILOVE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/chailove_libretro.so \
    $(TARGET_DIR)/usr/lib/libretro/chailove_libretro.so
endef

$(eval $(generic-package))
