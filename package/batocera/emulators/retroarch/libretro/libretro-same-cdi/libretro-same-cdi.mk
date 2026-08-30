################################################################################
#
# libretro-same-cdi
#
################################################################################
# Version: Commits on Aug 16, 2026
LIBRETRO_SAME_CDI_VERSION = 418be509a15342d3fc158a3e83c5b70c7940cd4b
LIBRETRO_SAME_CDI_SITE = $(call github,libretro,same_cdi,$(LIBRETRO_SAME_CDI_VERSION))
LIBRETRO_SAME_CDI_LICENSE = GPL
LIBRETRO_SAME_CDI_DEPENDENCIES += retroarch
LIBRETRO_SAME_CDI_EMULATOR_INFO = same_cdi.libretro.core.yml

# GCC 15 C++ / <cstdint> & sol2 -Wtemplate-body fixes
LIBRETRO_SAME_CDI_CXXFLAGS = $(TARGET_CXXFLAGS) -include cstdint -Wno-template-body

LIBRETRO_SAME_CDI_EXTRA_ARGS = platform=unix PTR64=1

define LIBRETRO_SAME_CDI_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) \
	CFLAGS="$(TARGET_CFLAGS)" \
	CXXFLAGS="$(LIBRETRO_SAME_CDI_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	$(LIBRETRO_SAME_CDI_EXTRA_ARGS) \
	-C $(@D) -f Makefile.libretro
endef

define LIBRETRO_SAME_CDI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/same_cdi_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/same_cdi_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
