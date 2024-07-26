################################################################################
#
# pironman
#
################################################################################

PIRONMAN_VERSION = 34b74f2a69b6a0b0c8867e2f830e569dd8eb6e12
PIRONMAN_SITE = $(call github,sunfounder,pironman,$(PIRONMAN_VERSION))
PIRONMAN_LICENSE = GPL-2.0
PIRONMAN_LICENSE_FILE = LICENSE

PIRONMAN_DEPENDENCIES += freetype getent i2c-tools libpng libxcb lirc-tools
PIRONMAN_DEPENDENCIES += net-tools openjpeg python-rpi-gpio python-rpi-ws281x
PIRONMAN_DEPENDENCIES += python-smbus-cffi python-spidev python3 tiff zlib rpi-eeprom

define PIRONMAN_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bin/pironman $(TARGET_DIR)/usr/bin/
	mkdir -p $(TARGET_DIR)/opt/pironman
	$(INSTALL) -D -m 0774 $(@D)/pironman/*.py $(TARGET_DIR)/opt/pironman/
	$(INSTALL) -D -m 0774 $(@D)/pironman/*.ttf $(TARGET_DIR)/opt/pironman/
	$(INSTALL) -D -m 0755 $(@D)/config.txt $(TARGET_DIR)/opt/pironman/
endef

$(eval $(generic-package))
