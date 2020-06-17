################################################################################
#
# kodi-platform
#
################################################################################

KODI18_PLATFORM_VERSION = 915da086fa7b4ea72796052a04ed6de95501b95c
KODI18_PLATFORM_SITE = $(call github,xbmc,kodi-platform,$(KODI18_PLATFORM_VERSION))
KODI18_PLATFORM_LICENSE = GPL-2.0+
KODI18_PLATFORM_LICENSE_FILES = debian/copyright
KODI18_PLATFORM_INSTALL_STAGING = YES
KODI18_PLATFORM_DEPENDENCIES = libplatform kodi18

$(eval $(cmake-package))
