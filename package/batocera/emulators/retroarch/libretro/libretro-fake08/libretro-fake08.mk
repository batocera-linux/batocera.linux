################################################################################
#
# libretro-fake08
#
################################################################################
# Version: Commits on Mar 11, 2022 (latest release)
LIBRETRO_FAKE08_VERSION = v0.0.2.20
LIBRETRO_FAKE08_SITE_METHOD=git
LIBRETRO_FAKE08_SITE=https://github.com/jtothebell/fake-08
LIBRETRO_FAKE08_LICENSE = MIT
LIBRETRO_FAKE08_GIT_SUBMODULES=YES

define LIBRETRO_FAKE08_BUILD_CMDS
	# $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile sdl2
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/platform/libretro -f Makefile platform="unix"
endef

define LIBRETRO_FAKE08_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/platform/libretro/fake08_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fake08_libretro.so
endef

$(eval $(generic-package))
