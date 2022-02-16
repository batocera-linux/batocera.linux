################################################################################
#
# umtool
#
################################################################################

UMTOOL_VERSION = 1665ad16a8fc4ca22181c54765fcc66650e299c3
UMTOOL_SITE = $(call github,katie-snow,Ultimarc-linux,$(UMTOOL_VERSION))
UMTOOL_LICENSE = GPLv2
UMTOOL_DEPENDENCIES = json-c libusb libtool udev
UMTOOL_CONF_OPTS = --disable-shared
UMTOOL_AUTORECONF = YES

define UMTOOL_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/src/umtool/umtool $(TARGET_DIR)/usr/bin/umtool

    # out-of-the-box configs
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/umtool
	cp $(@D)/src/umtool/*.json $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/umtool

	# udev rule
	cp $(@D)/21-ultimarc.rules $(TARGET_DIR)/etc/udev/rules.d/99-ultimarc.rules
endef

$(eval $(autotools-package))