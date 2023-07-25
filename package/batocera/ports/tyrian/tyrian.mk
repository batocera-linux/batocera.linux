################################################################################
#
# TYRIAN
#
################################################################################
# Version: Commits from March 18, 2022
TYRIAN_VERSION = v2.1.20220318
TYRIAN_SITE = $(call github,opentyrian,opentyrian,$(TYRIAN_VERSION))

TYRIAN_DEPENDENCIES = sdl2 sdl2_net

define TYRIAN_BUILD_CMDS
	# Cross-compile
	cd $(@D) && \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	PREFIX="$(STAGING_DIR)/usr" \
        PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
        PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	CPPFLAGS="-I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/SDL2 -lSDL2" \
	$(MAKE) PREFIX="$(STAGING_DIR)/usr"
endef

define TYRIAN_INSTALL_TARGET_CMDS
	#$(INSTALL) -D -m 0644 $(@D)/libTYRIAN.so $(TARGET_DIR)/usr/lib/libTYRIAN.so
	#$(INSTALL) -D -m 0755 $(@D)/TYRIAN $(TARGET_DIR)/usr/bin/TYRIAN
	#$(INSTALL) -D -m 0755 $(@D)/grid $(TARGET_DIR)/usr/bin/grid
endef

$(eval $(generic-package))
