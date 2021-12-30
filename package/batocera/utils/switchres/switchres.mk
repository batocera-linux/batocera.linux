################################################################################
#
# SwitchRes
#
################################################################################
# Version: Commits from Dec 27, 2021
SWITCHRES_VERSION = 5ea0efb278de119694a8128a6016821612422bde
SWITCHRES_SITE = $(call github,antonioginer,switchres,$(SWITCHRES_VERSION))

SWITCHRES_DEPENDENCIES = libdrm xserver_xorg-server
SWITCHRES_INSTALL_STAGING = YES

define SWITCHRES_BUILD_CMDS
	# Cross-compile standalone and libswitchres
	cd $(@D) && \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	PREFIX="$(STAGING_DIR)/usr" \
        PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
        PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	CPPFLAGS="-I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/SDL2 -I$(STAGING_DIR)/usr/include/drm -lSDL2" \
	$(MAKE) PREFIX="$(STAGING_DIR)/usr" all
endef

#	LDFLAGS="-lSDL2 -ldrm"

define SWITCHRES_INSTALL_STAGING_CMDS
	cd $(@D) && \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	BASE_DIR="" \
	PREFIX="$(STAGING_DIR)/usr" \
        PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
        PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	$(MAKE) install
endef

define SWITCHRES_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/libswitchres.so $(TARGET_DIR)/usr/lib/libswitchres.so
	$(INSTALL) -D -m 0755 $(@D)/switchres $(TARGET_DIR)/usr/bin/switchres
endef

$(eval $(generic-package))
