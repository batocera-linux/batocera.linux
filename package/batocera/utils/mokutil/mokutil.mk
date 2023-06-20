################################################################################
#
# mokutil
#
################################################################################

MOKUTIL_VERSION = 0.6.0
MOKUTIL_SITE = $(call github,lcp,mokutil,$(MOKUTIL_VERSION))
MOKUTIL_LICENSE = GPLv3
MOKUTIL_DEPENDENCIES = openssl efivar keyutils
MOKUTIL_AUTORECONF = YES

$(eval $(autotools-package))
