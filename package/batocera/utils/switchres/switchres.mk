################################################################################
#
# switchres
#
################################################################################

SWITCHRES_VERSION = 2.2.1
SWITCHRES_SITE = $(call github,antonioginer,switchres,v$(SWITCHRES_VERSION))
SWITCHRES_LICENSE = GPL-2.0+
SWITCHRES_DEPENDENCIES = libdrm sdl2 sdl2_ttf
SWITCHRES_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
SWITCHRES_DEPENDENCIES += xserver_xorg-server
endif

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
	$(INSTALL) -D -m 0644 $(@D)/libswitchres.so.$(SWITCHRES_VERSION) \
	    $(TARGET_DIR)/usr/lib/libswitchres.so.$(SWITCHRES_VERSION)
	ln -sf $(TARGET_DIR)/usr/lib/libswitchres.so.$(SWITCHRES_VERSION) \
	    $(TARGET_DIR)/usr/lib/libswitchres.so.2
	ln -sf $(TARGET_DIR)/usr/lib/libswitchres.so.2 \
	    $(TARGET_DIR)/usr/lib/libswitchres.so
	$(INSTALL) -D -m 0755 $(@D)/switchres $(TARGET_DIR)/usr/bin/switchres
	$(INSTALL) -D -m 0755 $(@D)/grid $(TARGET_DIR)/usr/bin/grid

	$(INSTALL) -D -m 0644 $(@D)/switchres.ini $(TARGET_DIR)/etc/switchres.ini
	(echo "#!/usr/bin/env python"; echo; cat $(@D)/geometry.py) > $(TARGET_DIR)/usr/bin/geometry
	chmod 755 $(TARGET_DIR)/usr/bin/geometry
endef

$(eval $(generic-package))
