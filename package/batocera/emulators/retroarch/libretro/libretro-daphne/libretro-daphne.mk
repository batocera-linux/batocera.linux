################################################################################
#
# DAPHNE
#
################################################################################
# Version.: Commits on Aug 17, 2019
LIBRETRO_DAPHNE_VERSION = c1f7d09c8b3a9bf17b28bd5a123635fb6784f8ba
LIBRETRO_DAPHNE_SITE = $(call github,libretro,daphne,$(LIBRETRO_DAPHNE_VERSION))

define LIBRETRO_DAPHNE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="unix"
endef

define LIBRETRO_DAPHNE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/daphne_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/daphne_libretro.so
endef

$(eval $(generic-package))
