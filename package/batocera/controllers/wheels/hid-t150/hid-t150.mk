################################################################################
#
# hid-t150
#
################################################################################
# Version: Commits on Feb 26, 2025
HID_T150_VERSION = f7ecb30c65ee5f7870e921bc0a2354df8e1e8100
HID_T150_SITE = $(call github,scarburato,t150_driver,$(HID_T150_VERSION))
HID_T150_MODULE_SUBDIRS = hid-t150

$(eval $(kernel-module))
$(eval $(generic-package))
