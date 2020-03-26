################################################################################
#
# SLANG SHADERS
#
################################################################################
# Version.: Commits on Feb 24, 2019
SLANG_SHADERS_VERSION = 9850d68939b86262eae9f0da01ff1c11daafcdc3
SLANG_SHADERS_SITE = $(call github,libretro,slang-shaders,$(SLANG_SHADERS_VERSION))
SLANG_SHADERS_LICENSE = GPL

define SLANG_SHADERS_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile
endef

define SLANG_SHADERS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) INSTALLDIR=$(TARGET_DIR)/usr/share/batocera/shaders install
endef

$(eval $(generic-package))
