################################################################################
#
# CAP32
#
################################################################################
# Version.: Commits on Jan 28, 2019
LIBRETRO_CAP32_VERSION = 1a8bcf4d68b633bb8e92e20da460ac7618e8b950
LIBRETRO_CAP32_SITE = $(call github,libretro,libretro-cap32,$(LIBRETRO_CAP32_VERSION))
LIBRETRO_CAP32_LICENSE="GPLv2"

define LIBRETRO_CAP32_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile
endef

define LIBRETRO_CAP32_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/cap32_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/cap32_libretro.so
endef

$(eval $(generic-package))
