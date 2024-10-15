################################################################################
#
# libretro-fake08
#
################################################################################
# Version: Commits on Sept 2, 2024
LIBRETRO_FAKE08_VERSION = 0d26fd59103941e5f95e0ee665c6e0fb8c6b6f03
LIBRETRO_FAKE08_SITE_METHOD=git
LIBRETRO_FAKE08_SITE=https://github.com/jtothebell/fake-08
LIBRETRO_FAKE08_LICENSE = MIT
LIBRETRO_FAKE08_GIT_SUBMODULES=YES

define LIBRETRO_FAKE08_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/platform/libretro -f Makefile platform="unix"
endef

define LIBRETRO_FAKE08_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/platform/libretro/fake08_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fake08_libretro.so
endef

$(eval $(generic-package))
