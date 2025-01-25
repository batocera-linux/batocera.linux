################################################################################
#
# slang-shaders
#
################################################################################
# Version: Commits on Jul 31, 2024
SLANG_SHADERS_VERSION = 679a3321c104342e81658819fcb2dc37143d4ad7
SLANG_SHADERS_SITE = $(call github,libretro,slang-shaders,$(SLANG_SHADERS_VERSION))
SLANG_SHADERS_LICENSE = GPL

define SLANG_SHADERS_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" \
	CXXFLAGS="$(TARGET_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" \
	    CC="$(TARGET_CC)" -C $(@D)/ -f Makefile
endef

define SLANG_SHADERS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) \
	    INSTALLDIR=$(TARGET_DIR)/usr/share/batocera/shaders install
endef

define SLANG_SHADERS_BATOCERA_SHADERS_SLANG
    # Some shaders got the .slan(g) variants moved
    mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders/interpolation/shaders
    mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders/scalehq/shaders
    cd $(TARGET_DIR)/usr/share/batocera/shaders/ && cp -f pixel-art-scaling/sharp-bilinear-simple.slangp ./interpolation/ && \
		cp -f pixel-art-scaling/shaders/sharp-bilinear-simple.slang ./interpolation/shaders/
    cd $(TARGET_DIR)/usr/share/batocera/shaders/ && cp -f edge-smoothing/scalehq/2xScaleHQ.slangp ./scalehq/ && \
		cp -f ./edge-smoothing/scalehq/shaders/2xScaleHQ.slang ./scalehq/shaders/
endef

ifeq ($(BR2_PACKAGE_BATOCERA_SHADERS),y)
    SLANG_SHADERS_POST_INSTALL_TARGET_HOOKS = SLANG_SHADERS_BATOCERA_SHADERS_SLANG
endif

$(eval $(generic-package))
