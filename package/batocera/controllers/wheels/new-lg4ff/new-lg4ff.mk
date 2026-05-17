################################################################################
#
# new-lg4ff
#
################################################################################
# Version: Commits on May 29, 2025
NEW_LG4FF_VERSION = 2092db19f7b40854e0427a1b2e39eda9f8d0c3cd
NEW_LG4FF_SITE = $(call github,berarma,new-lg4ff,$(NEW_LG4FF_VERSION))

# requires CONFIG_HID_LOGITECH kernel modules
NEW_LG4FF_MODULE_MAKE_OPTS = \
	CONFIG_USB_HID=y \
	CONFIG_LEDS_CLASS=y \
	CONFIG_LEDS_CLASS_MULTICOLOR=y \
	CONFIG_HID_LOGITECH=m \
	CONFIG_HID_LOGITECH_DJ=m \
	CONFIG_HID_LOGITECH_HIDPP=m \
	CONFIG_LOGITECH_FF=y

$(eval $(kernel-module))
$(eval $(generic-package))
