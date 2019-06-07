################################################################################
#
# UNCLUTTER - A rewrite of unclutter using the x11-xfixes extension
#
################################################################################

# Version: 1.5
UNCLUTTER_VERSION = 10fd337bb77e4e93c3380f630a0555372778a948
UNCLUTTER_LICENSE = MIT
UNCLUTTER_SITE = $(call github,Airblader,unclutter-xfixes,$(UNCLUTTER_VERSION))
UNCLUTTER_DEPENDENCIES = xserver_xorg-server libev

UNCLUTTER_CFLAGS="-I$(@D)/include"
UNCLUTTER_LDFLAGS="-lev -lX11 -lXi -lXfixes"

define UNCLUTTER_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D) \
		CFLAGS=$(UNCLUTTER_CFLAGS) LDFLAGS=$(UNCLUTTER_LDFLAGS) unclutter
endef

define UNCLUTTER_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/unclutter $(TARGET_DIR)/usr/bin/unclutter
endef

$(eval $(generic-package))
