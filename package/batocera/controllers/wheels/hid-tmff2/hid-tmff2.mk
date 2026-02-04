################################################################################
#
# hid-tmff2
#
################################################################################
# Version: Commits on Jan 26, 2026
HID_TMFF2_VERSION = 66e522e26549afab26d032e900ae9f6576c83b9d
HID_TMFF2_SITE = $(call github,Kimplul,hid-tmff2,$(HID_TMFF2_VERSION))

$(eval $(kernel-module))
$(eval $(generic-package))
