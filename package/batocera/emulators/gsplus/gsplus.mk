################################################################################
#
# GS+
#
################################################################################
# Version.: Commits on Aug 16, 2019
GSPLUS_VERSION = 480572054518112647c8fae5d7ea7046a6d6ecfb
GSPLUS_SITE = $(call github,digarok,gsplus,$(GSPLUS_VERSION))
GSPLUS_LICENSE = GPLv2
GSPLUS_DEPENDENCIES = sdl2 libpcap

define GSPLUS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bin/GSplus $(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/bin/libx_readline.so $(TARGET_DIR)/usr/lib/
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/gsplus/apple2gs.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
