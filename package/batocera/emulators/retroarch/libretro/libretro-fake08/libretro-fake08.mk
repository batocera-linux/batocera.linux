################################################################################
#
# libretro-fake08
#
################################################################################
# Version: Commits on Jan 19, 2026
LIBRETRO_FAKE08_VERSION = f6bab5a7ba521ce440e45d1aeef6122674be6ee9
LIBRETRO_FAKE08_SITE_METHOD=git
LIBRETRO_FAKE08_SITE=https://github.com/jtothebell/fake-08
LIBRETRO_FAKE08_LICENSE = MIT
LIBRETRO_FAKE08_GIT_SUBMODULES=YES
LIBRETRO_FAKE08_DEPENDENCIES += retroarch
LIBRETRO_FAKE08_EMULATOR_INFO = fake08.libretro.core.yml

define LIBRETRO_FAKE08_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/platform/libretro -f Makefile platform="unix"
endef

define LIBRETRO_FAKE08_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/platform/libretro/fake08_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fake08_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))