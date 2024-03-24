################################################################################
#
# gpicase
#
################################################################################
GPICASE_VERSION = 2.1
GPICASE_SOURCE =

define GPICASE_INSTALL_TARGET_CMDS
	mkdir -p $(BINARIES_DIR)/rpi-firmware/overlays
	cp -rf $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/cases/gpicase/overlays/*			$(BINARIES_DIR)/rpi-firmware/overlays/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/cases/gpicase/99-gpicase.rules		$(TARGET_DIR)/etc/udev/rules.d/

	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/cases/gpicase/batocera-gpicase-install	$(TARGET_DIR)/usr/bin/batocera-gpicase-install
endef

$(eval $(generic-package))
