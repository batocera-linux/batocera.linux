################################################################################
#
# xpadneo
#
################################################################################

XPADNEO_VERSION = 1187253a4da9adb444e81c758bf081da5c944b21
XPADNEO_SITE = $(call github,atar-axis,xpadneo,$(XPADNEO_VERSION))
XPADNEO_DEPENDENCIES = host-libcurl host-cabextract bluez5_utils
XPADNEO_MODULE_SUBDIRS = hid-xpadneo/src

define XPADNEO_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib/udev/rules.d
	cp -v $(@D)/hid-xpadneo/etc-udev-rules.d/*.rules $(TARGET_DIR)/etc/udev/rules.d/
	cp -v $(@D)/hid-xpadneo/etc-modprobe.d/*.conf $(TARGET_DIR)/etc/modprobe.d/
	echo "options hid_xpadneo trigger_rumble_mode=2" >> $(TARGET_DIR)/etc/modprobe.d/xpadneo.conf
	echo "options bluetooth disable_ertm=1" >> $(TARGET_DIR)/etc/modprobe.d/xpadneo.conf
endef

$(eval $(kernel-module))
$(eval $(generic-package))
