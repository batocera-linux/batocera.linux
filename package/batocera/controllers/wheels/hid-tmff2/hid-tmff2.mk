################################################################################
#
# hid-tmff2
#
################################################################################
# Version: Commits on Feb 3, 2025
HID_TMFF2_VERSION = a9312ead5720922e1c06b541ea48b6db3f289d36
HID_TMFF2_SITE = $(call github,Kimplul,hid-tmff2,$(HID_TMFF2_VERSION))

$(eval $(kernel-module))
$(eval $(generic-package))
