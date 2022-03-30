################################################################################
#
# SwitchRes
#
################################################################################
# Version: Commits from Jan 11th, 2022
SWITCHRES_VERSION = f3144602949ccb93ac2705aa9a89c18bd26fe8cc
SWITCHRES_SITE = $(call github,antonioginer,switchres,$(SWITCHRES_VERSION))

SWITCHRES_DEPENDENCIES = libdrm xserver_xorg-server
SWITCHRES_INSTALL_STAGING = YES

define SWITCHRES_BUILD_CMDS
	# Cross-compile standalone and libswitchres
	cd $(@D) && \
        PATH="$(HOST_DIR)/bin:$$PATH" \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	PREFIX="$(STAGING_DIR)/usr" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	CPPFLAGS="-I$(STAGING_DIR)/usr/include -I$(STAGING_DIR)/usr/include/libdrm" \
	$(MAKE) all grid
endef

define SWITCHRES_INSTALL_STAGING_CMDS
	cd $(@D) && \
        PATH="$(HOST_DIR)/bin:$$PATH" \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	BASE_DIR="" \
	PREFIX="$(STAGING_DIR)/usr" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	$(MAKE) install
endef

define SWITCHRES_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/libswitchres.so $(TARGET_DIR)/usr/lib/libswitchres.so
	$(INSTALL) -D -m 0755 $(@D)/switchres $(TARGET_DIR)/usr/bin/switchres
	$(INSTALL) -D -m 0755 $(@D)/grid $(TARGET_DIR)/usr/bin/grid
endef

$(eval $(generic-package))
