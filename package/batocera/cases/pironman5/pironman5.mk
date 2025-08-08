################################################################################
#
# pironman5
#
################################################################################

PIRONMAN5_VERSION = 1.2.15
PIRONMAN5_SITE = $(call github,sunfounder,pironman5,$(PIRONMAN5_VERSION))
PIRONMAN5_SETUP_TYPE = setuptools
PIRONMAN5_LICENSE = GPL-2.0
PIRONMAN5_LICENSE_FILE = LICENSE

PIRONMAN5_DEPENDENCIES += python-influxdb freetype i2c-tools kmod python-numpy
PIRONMAN5_DEPENDENCIES += python-gpiozero pm_auto sf_rpi_status rpi-eeprom

define PIRONMAN5_INSTALL_OVERLAY
    $(INSTALL) -D -m 0755 $(@D)/bin/pironman5 $(TARGET_DIR)/usr/bin/
	mkdir -p $(BINARIES_DIR)/pironman5/
	$(INSTALL) -D -m 0644 $(@D)/sunfounder-pironman5*.dtbo $(BINARIES_DIR)/pironman5/
	# copy our default config.json
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/pironman5
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/cases/pironman5/config.json \
	    $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/pironman5/
	# create a symbolic link to userdata to avoid multiple config.json files
	ln -sf /userdata/system/configs/pironman5/config.json \
	    $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/pironman5/config.json
endef

PIRONMAN5_POST_INSTALL_TARGET_HOOKS = PIRONMAN5_INSTALL_OVERLAY

$(eval $(python-package))
