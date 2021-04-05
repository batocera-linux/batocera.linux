################################################################################
#
# COMMON SHADERS
#
################################################################################
# Version.: Commits on Feb 26, 2021
COMMON_SHADERS_VERSION = 55e401834b732e62c34411321c4ffd82524345d4
COMMON_SHADERS_SITE = $(call github,libretro,common-shaders,$(COMMON_SHADERS_VERSION))
COMMON_SHADERS_LICENSE = GPL

define COMMON_SHADERS_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile
endef

define COMMON_SHADERS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) INSTALLDIR=$(TARGET_DIR)/usr/share/batocera/shaders install
endef

$(eval $(generic-package))
