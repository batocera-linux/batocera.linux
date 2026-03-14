################################################################################
#
# pironman
#
################################################################################
# Version: [2.2.9] - 2024-7-23
PIRONMAN_VERSION = 997c361ed71fff859d832e171f63180fbbb4e314
PIRONMAN_SITE = $(call github,sunfounder,pironman,$(PIRONMAN_VERSION))
PIRONMAN_LICENSE = GPL-2.0
PIRONMAN_LICENSE_FILE = LICENSE

PIRONMAN_DEPENDENCIES += freetype getent i2c-tools libpng libxcb lirc-tools
PIRONMAN_DEPENDENCIES += net-tools openjpeg python-gpiozero python-lgpio python-rpi-ws281x
PIRONMAN_DEPENDENCIES += python-smbus-cffi python-spidev python3 tiff zlib rpi-eeprom

define PIRONMAN_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bin/pironman $(TARGET_DIR)/usr/bin/
	mkdir -p $(TARGET_DIR)/opt/pironman
	$(INSTALL) -D -m 0774 $(@D)/pironman/*.py $(TARGET_DIR)/opt/pironman/
	$(INSTALL) -D -m 0774 $(@D)/pironman/*.ttf $(TARGET_DIR)/opt/pironman/
	$(INSTALL) -D -m 0755 $(@D)/config.txt $(TARGET_DIR)/opt/pironman/
endef

$(eval $(generic-package))
