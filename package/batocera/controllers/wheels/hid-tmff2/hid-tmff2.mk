################################################################################
#
# hid-tmff2
#
################################################################################
# Version: Commits on Aug 25, 2026
HID_TMFF2_VERSION = d890a93105a0aa52028ac49282fa1b579e12566e
HID_TMFF2_SITE = $(call github,Kimplul,hid-tmff2,$(HID_TMFF2_VERSION))

$(eval $(kernel-module))
$(eval $(generic-package))
