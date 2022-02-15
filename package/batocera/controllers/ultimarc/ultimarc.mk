################################################################################
#
# Ultimarc-linux
#
################################################################################

ULTIMARC_VERSION = 1665ad16a8fc4ca22181c54765fcc66650e299c3
ULTIMARC_SITE = $(call github,katie-snow,Ultimarc-linux,$(ULTIMARC_VERSION))
ULTIMARC_LICENSE = GPLv2
ULTIMARC_DEPENDENCIES = json-c libusb libtool udev
ULTIMARC_CONF_OPTS = --disable-shared
ULTIMARC_AUTORECONF = YES

define ULTIMARC_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/src/umtool/umtool $(TARGET_DIR)/usr/bin/umtool

    # out-of-the-box configs
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/umtool
	cp $(@D)/src/umtool/*.json $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/umtool

	# udev rule
	cp $(@D)/21-ultimarc.rules $(TARGET_DIR)/etc/udev/rules.d/99-ultimarc.rules
endef

$(eval $(autotools-package))