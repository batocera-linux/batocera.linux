################################################################################
#
# UNCLUTTER - Hide X11 Cursor
#
################################################################################

UNCLUTTER_VERSION = 1.09
UNCLUTTER_SOURCE = unclutter-$(UNCLUTTER_VERSION).tar.gz
UNCLUTTER_SITE = https://netassist.dl.sourceforge.net/project/unclutter/unclutter/source_$(UNCLUTTER_VERSION)
UNCLUTTER_DEPENDENCIES = xserver_xorg-server

define UNCLUTTER_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D) \
		CFLAGS="$(UNCLUTTER_TARGET_CFLAGS) $(UNCLUTTER_CFLAGS)" \
		AS="$(TARGET_CC) -c"
endef

define UNCLUTTER_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/unclutter $(TARGET_DIR)/usr/bin/unclutter
endef

$(eval $(generic-package))
