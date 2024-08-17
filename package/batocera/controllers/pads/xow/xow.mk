################################################################################
#
# xow
#
################################################################################
# Version.: Commits on Apr 24, 2022
XOW_VERSION = d335d6024f8380f52767a7de67727d9b2f867871
XOW_SITE = $(call github,medusalix,xow,$(XOW_VERSION))
XOW_DEPENDENCIES = host-libcurl host-cabextract libusb

define XOW_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CC="$(TARGET_CC)" -C  $(@D)
endef

define XOW_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/xow $(TARGET_DIR)/usr/bin/xow
	$(INSTALL) -m 0755 -D $(@D)/install/modprobe.conf $(TARGET_DIR)/etc/modprobe.d/xow-blacklist.conf
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/xow/xow-daemon $(TARGET_DIR)/usr/bin/xow-daemon
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/xow/99-xow.rules $(TARGET_DIR)/etc/udev/rules.d
endef

$(eval $(generic-package))
