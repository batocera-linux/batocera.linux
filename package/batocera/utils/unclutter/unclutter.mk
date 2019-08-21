################################################################################
#
# UNCLUTTER - A rewrite of unclutter using the x11-xfixes extension
#
################################################################################

# Version: 1.5-batocera
UNCLUTTER_VERSION = v1.5-batocera
UNCLUTTER_LICENSE = MIT
UNCLUTTER_SITE = $(call github,batocera-linux,unclutter-xfixes,$(UNCLUTTER_VERSION))
UNCLUTTER_DEPENDENCIES = xserver_xorg-server libev

UNCLUTTER_CFLAGS="-I$(@D)/include -D'__VERSION=\"$(UNCLUTTER_VERSION)\"'"
UNCLUTTER_LDFLAGS="-lev -lX11 -lXi -lXfixes"

define UNCLUTTER_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D) \
		CFLAGS=$(UNCLUTTER_CFLAGS) LDFLAGS=$(UNCLUTTER_LDFLAGS) unclutter
endef

define UNCLUTTER_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/unclutter $(TARGET_DIR)/usr/bin/unclutter
	$(INSTALL) -D $(@D)/bin/unclutter-remote $(TARGET_DIR)/usr/bin/unclutter-remote
endef

$(eval $(generic-package))
