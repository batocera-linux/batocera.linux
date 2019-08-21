################################################################################
#
# android-headers
#
#
################################################################################

ANDROID_HEADERS_VERSION = 25
ANDROID_HEADERS_SOURCE = android-headers-$(ANDROID_HEADERS_VERSION).tar.gz
ANDROID_HEADERS_SITE = http://sources.libreelec.tv/mirror/android-headers

ANDROID_HEADERS_INSTALL_STAGING = YES

$(eval $(generic-package))
