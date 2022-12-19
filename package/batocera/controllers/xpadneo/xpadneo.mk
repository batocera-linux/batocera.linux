################################################################################
#
# xpadneo
#
################################################################################

XPADNEO_VERSION = v0.9.5
XPADNEO_SITE = $(call github,atar-axis,xpadneo,$(XPADNEO_VERSION))
XPADNEO_DEPENDENCIES = host-libcurl host-cabextract bluez5_utils
XPADNEO_MODULE_SUBDIRS = hid-xpadneo/src

define XPADNEO_INSTALL_TARGET_CMDS
	cp -v $(@D)/hid-xpadneo/etc-udev-rules.d/*.rules $(TARGET_DIR)/etc/udev/rules.d/
	cp -v $(@D)/hid-xpadneo/etc-modprobe.d/*.conf $(TARGET_DIR)/etc/modprobe.d/
	echo "options bluetooth disable_ertm=1" >> $(TARGET_DIR)/etc/modprobe.d/xpadneo.conf
endef

$(eval $(kernel-module))
$(eval $(generic-package))
