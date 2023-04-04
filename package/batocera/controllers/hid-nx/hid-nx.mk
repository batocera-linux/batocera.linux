################################################################################
#
# hid-nx
#
################################################################################

HID_NX_VERSION = 974d6c407296c47390d99f008933846c86f52bb9
HID_NX_SITE = $(call github,emilyst,hid-nx-dkms,$(HID_NX_VERSION))
HID_NX_DEPENDENCIES = host-libcurl host-cabextract libusb

define HID_NX_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/etc/udev/rules.d
	cp -v $(@D)/99-joycond-ignore.rules $(TARGET_DIR)/etc/udev/rules.d/
	# blacklist hid-nintendo
	mkdir -p $(TARGET_DIR)/etc/modprobe.d
	echo "blacklist hid-nintendo" > $(TARGET_DIR)/etc/modprobe.d/hid-nintendo.conf
endef

$(eval $(kernel-module))
$(eval $(generic-package))
