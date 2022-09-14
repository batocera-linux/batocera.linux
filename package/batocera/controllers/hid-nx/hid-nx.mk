################################################################################
#
# hid-nx
#
################################################################################

HID_NX_VERSION = 7496b6e7074ccd0cf8951f8c5de663bdf2af7ef9
HID_NX_SITE = $(call github,emilyst,hid-nx-dkms,$(HID_NX_VERSION))
HID_NX_DEPENDENCIES = host-libcurl host-cabextract libusb

define HID_NX_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/etc/udev/rules.d
	cp -v $(@D)/99-joycond-ignore.rules $(TARGET_DIR)/etc/udev/rules.d/
endef

$(eval $(kernel-module))
$(eval $(generic-package))
