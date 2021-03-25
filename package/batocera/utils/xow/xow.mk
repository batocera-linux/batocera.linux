################################################################################
#
# xow
#
################################################################################
XOW_VERSION = cd271644ead198dcbfeafd3c3411092850adfd3a
XOW_SITE = $(call github,medusalix,xow,$(XOW_VERSION))
XOW_DEPENDENCIES = host-libcurl host-cabextract libusb

define XOW_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CC="$(TARGET_CC)" -C  $(@D)
endef

define XOW_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(@D)/xow $(TARGET_DIR)/usr/bin/xow
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/xow/xow-daemon $(TARGET_DIR)/usr/bin/xow-daemon
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/xow/99-xow.rules $(TARGET_DIR)/etc/udev/rules.d
endef

$(eval $(generic-package))
