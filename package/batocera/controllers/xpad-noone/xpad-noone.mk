################################################################################
#
# xpad-noone
#
################################################################################

XPAD_NOONE_VERSION = d9974e0f03bfb90ad0cf783a59de8e8f14c1a8e8
XPAD_NOONE_SITE = $(call github,medusalix,xpad-noone,$(XPAD_NOONE_VERSION))
XPAD_NOONE_DEPENDENCIES = host-libcurl host-cabextract libusb

XPAD_NOONE_USER_EXTRA_CFLAGS = -w -Wno-error=unused-function

XPAD_NOONE_MODULE_MAKE_OPTS = \
	KCFLAGS="$$KCFLAGS $(XPAD_NOONE_USER_EXTRA_CFLAGS)"

$(eval $(kernel-module))
$(eval $(generic-package))
