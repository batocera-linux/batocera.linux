################################################################################
#
# hid-t150
#
################################################################################
# Version: Commits on Dec 19, 2023
HID_T150_VERSION = 580b79b7b479076ba470fcc21fbd8484f5328546
HID_T150_SITE = $(call github,scarburato,t150_driver,$(HID_T150_VERSION))
HID_T150_MODULE_SUBDIRS = hid-t150

$(eval $(kernel-module))
$(eval $(generic-package))
