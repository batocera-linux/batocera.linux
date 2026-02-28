################################################################################
#
# gpicase
#
################################################################################

GPICASE_VERSION = 2.1
GPICASE_SOURCE =
GPICASE_INSTALL_IMAGES = YES

define GPICASE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/etc/udev/rules.d/
	cp $(GPICASE_PKGDIR)/99-gpicase.rules $(TARGET_DIR)/etc/udev/rules.d/
	$(INSTALL) -m 0755 $(GPICASE_PKGDIR)/batocera-gpicase-install $(TARGET_DIR)/usr/bin/batocera-gpicase-install
endef

define GPICASE_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/rpi-firmware/overlays
	cp -rf $(GPICASE_PKGDIR)/overlays/* $(BINARIES_DIR)/rpi-firmware/overlays/
endef

$(eval $(generic-package))
